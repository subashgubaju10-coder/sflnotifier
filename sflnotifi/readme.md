# SFL Community Farm Timers

A simple webpage that displays active timers from the Sunflower Land community farm API.

## Usage

Start the proxy server and open the page in your browser:

```bash
python server.py
```

Then open:

```text
http://localhost:8000/index.html
```

## API

This project now uses the Sunflower Land community farm endpoint:

`https://api.sunflower-land.com/community/farms/2764070498485257`

The proxy server forwards the request with the API key from the widget-style configuration.

## Features

- Shows VIP expiration timers
- Parses crop harvest timers from planted crops
- Parses tree, stone, iron, gold, crimstone, sunstone, and oil recovery timers
- Shows power cooldown timers for bumpkin powers
- Includes greenhouse, flower, fruit, and mushroom timers when available
- Shows daily reset timers for daily rewards and pirate chest
- Updates countdowns every second
- Displays the full raw API response

## Run locally

1. Start the proxy server:

```bash
python server.py
```

2. Open the page in a browser:

```text
http://localhost:8000/index.html
```

The page fetches data through the local proxy at `/api/farm`, avoiding browser CORS restrictions and keeping your API key hidden from the browser.

## Note

This page now uses the same Sunflower Land farm API source that `SFL_widget.js` expects. It will display timers for items included in that community farm response.
