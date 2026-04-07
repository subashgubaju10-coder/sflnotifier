import urllib.request

for path in ['/api/farm', '/api/farm2', '/api/farm3']:
    try:
        with urllib.request.urlopen(f'http://localhost:9000{path}', timeout=20) as r:
            print(path, r.status, r.getheader('X-Cache'), len(r.read()))
    except Exception as e:
        print(path, 'ERROR', type(e).__name__, e)
