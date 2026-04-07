import http.server
import socketserver
import urllib.request
import urllib.error
import json
import time
import threading
from urllib.parse import urlparse

API_KEY = 'sfl.Mjc2NDA3MDQ5ODQ4NTI1Nw.FDeuCnUemIV2fm0mdLWfLhy_tuhVxlyU5XwaHpHd6bM'
FARM_ID = '2764070498485257'
API_URL = f'https://api.sunflower-land.com/community/farms/{FARM_ID}'

API_KEY2 = 'sfl.ODA3NTY2MTY4MzEyODYyNw.RkTp34CtcP5cHziChUigEfjEiSqzYWlvbw62mmoONoI'
FARM_ID2 = '8075661683128627'
API_URL2 = f'https://api.sunflower-land.com/community/farms/{FARM_ID2}'

API_KEY3 = 'sfl.MzMxNTQ5NzcxNTUzNDMwOQ.4qg5RsD_wwS9y7dtRR0s29YLSpMB0JsadyF0Gpk41oc'
FARM_ID3 = '3315497715534309'
API_URL3 = f'https://api.sunflower-land.com/community/farms/{FARM_ID3}'
AUCTIONS_URL = 'https://sfl.world/api/v1/auctions'
PORT = 9000

# Cache configuration
CACHE_DURATION = 120  # Cache responses for 120 seconds
cache = {}
last_request_time = {}
request_lock = threading.Lock()

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/farm':
            self.fetch_farm(API_URL, API_KEY, 'farm1')
        elif parsed.path == '/api/farm2':
            self.fetch_farm(API_URL2, API_KEY2, 'farm2')
        elif parsed.path == '/api/farm3':
            self.fetch_farm(API_URL3, API_KEY3, 'farm3')
        elif parsed.path == '/api/auctions':
            self.fetch_auctions()
        else:
            super().do_GET()

    def fetch_farm(self, api_url, api_key, cache_key):
        with request_lock:
            # Check if we have cached data
            if cache_key in cache:
                cached_data, cached_time = cache[cache_key]
                if time.time() - cached_time < CACHE_DURATION:
                    # Return cached data
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('X-Cache', 'hit')
                    self.send_header('Content-Length', str(len(cached_data)))
                    self.end_headers()
                    self.wfile.write(cached_data)
                    print(f'[{cache_key}] Served from cache')
                    return
            
            # Check if we recently made a request to avoid rate limiting
            if cache_key in last_request_time:
                time_since_last = time.time() - last_request_time[cache_key]
                if time_since_last < 30:  # Wait at least 30 seconds between requests
                    if cache_key in cache:
                        cached_data, _ = cache[cache_key]
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('X-Cache', 'stale')
                        self.send_header('Content-Length', str(len(cached_data)))
                        self.end_headers()
                        self.wfile.write(cached_data)
                        print(f'[{cache_key}] Served stale cache (throttled)')
                        return
        
        try:
            request = urllib.request.Request(
                api_url,
                headers={
                    'x-api-key': api_key,
                    'Accept': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
                }
            )
            with urllib.request.urlopen(request, timeout=20) as response:
                body = response.read()
                
                # Cache the successful response
                with request_lock:
                    cache[cache_key] = (body, time.time())
                    last_request_time[cache_key] = time.time()
                
                self.send_response(response.getcode())
                self.send_header('Content-Type', 'application/json')
                self.send_header('X-Cache', 'miss')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                print(f'[{cache_key}] Fresh data from API (200)')
        except urllib.error.HTTPError as error:
            # If rate limited, return cached data if available
            if error.code == 429:
                with request_lock:
                    if cache_key in cache:
                        cached_data, _ = cache[cache_key]
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('X-Cache', 'expired')
                        self.send_header('Content-Length', str(len(cached_data)))
                        self.end_headers()
                        self.wfile.write(cached_data)
                        print(f'[{cache_key}] Rate limited, served expired cache')
                        return
            
            # No cached data, return the error
            body = error.read() if hasattr(error, 'read') else b''
            self.send_response(error.code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            message = {
                'error': error.reason,
                'status': error.code,
                'body': body.decode('utf-8', errors='replace')
            }
            self.wfile.write(json.dumps(message).encode('utf-8'))
            print(f'[{cache_key}] Error: {error.code}')
        except Exception as error:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            message = {
                'error': str(error)
            }
            self.wfile.write(json.dumps(message).encode('utf-8'))
            print(f'[{cache_key}] Exception: {error}')

    def fetch_auctions(self):
        cache_key = 'auctions'
        with request_lock:
            # Check if we have cached data
            if cache_key in cache:
                cached_data, cached_time = cache[cache_key]
                if time.time() - cached_time < CACHE_DURATION:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('X-Cache', 'hit')
                    self.send_header('Content-Length', str(len(cached_data)))
                    self.end_headers()
                    self.wfile.write(cached_data)
                    print(f'[{cache_key}] Served from cache')
                    return

        try:
            request = urllib.request.Request(
                AUCTIONS_URL,
                headers={
                    'Accept': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                    'Referer': 'https://sfl.world/',
                    'Origin': 'https://sfl.world'
                }
            )
            with urllib.request.urlopen(request, timeout=20) as response:
                body = response.read()
                with request_lock:
                    cache[cache_key] = (body, time.time())
                self.send_response(response.getcode())
                self.send_header('Content-Type', 'application/json')
                self.send_header('X-Cache', 'miss')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                print(f'[{cache_key}] Fresh data from API')
        except urllib.error.HTTPError as error:
            print(f'[{cache_key}] HTTP Error: {error.code} - {error.reason}')
            # Return empty array on 403/404 instead of error
            if error.code in [403, 404]:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                empty_result = json.dumps({'list': [], 'message': 'No auctions available'})
                self.wfile.write(empty_result.encode('utf-8'))
                print(f'[{cache_key}] Returned empty result (access denied)')
            else:
                self.send_response(error.code)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                message = {
                    'error': error.reason,
                    'status': error.code
                }
                self.wfile.write(json.dumps(message).encode('utf-8'))
        except Exception as error:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            message = {
                'error': str(error)
            }
            self.wfile.write(json.dumps(message).encode('utf-8'))
            print(f'[{cache_key}] Exception: {error}')

if __name__ == '__main__':
    with socketserver.TCPServer(('0.0.0.0', PORT), ProxyHTTPRequestHandler) as httpd:
        print(f'Serving at http://localhost:{PORT}')
        httpd.serve_forever()
