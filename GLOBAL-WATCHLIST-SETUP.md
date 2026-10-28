# Global AI Stocks Watchlist — Version 1

## What is implemented in the repository

- `data/global-ai-watchlist-v1.json`: starter universe of AI-related publicly traded companies grouped by AI industry category.
- `global-watchlist.html`: browser dashboard with company/ticker search, AI category filter, favorites-only view, and browser-local favorite persistence.
- The dashboard intentionally displays no stock prices until a market-data provider is connected. It does not invent prices.

## Run locally on Windows

1. Download or clone this repository to your Windows computer.
2. Open Command Prompt in the repository folder (the folder containing this file and `index.html`).
3. Confirm Python is installed with `py --version`.
4. Start the local web server:

   ```bat
   py -m http.server 3000
   ```

5. On the same computer, open this URL in a browser:

   ```
   http://localhost:3000/global-watchlist.html
   ```

6. Try searching for `NVIDIA`, filtering to a category, starring a ticker, refreshing the page, and selecting Favorites only. Favorites should persist in that browser.

If `py` is not recognized, try `python --version` and then `python -m http.server 3000`.

## Current limitations

- This is a starter universe, not an exhaustive inventory of every AI-related public company worldwide.
- Symbols, exchange mappings, listings, and the strength of each company's AI exposure must be verified with the selected market-data source.
- No market-data provider or quote API is connected yet; prices, changes, volumes, quote timestamps, AI signals, alerts, and background monitoring are not live.
- Favorites are stored in the current browser only, not synced between devices.
- No orders are placed. Paper trading and live brokerage connections are not implemented by this watchlist page.
- Free quote APIs have request limits, market coverage gaps, and may delay quotes. The app must show the source and freshness/delay status when the feed is added.

## Next implementation stage

1. Choose a free-first provider with documented access for the target exchanges.
2. Build a provider adapter that returns normalized ticker, currency, price, change, source, timestamp, and delay status.
3. Validate a sample across US, Japan, South Korea, Hong Kong, and European listings.
4. Handle provider limits, missing quotes, closed markets, stale data, and errors visibly.
5. Only after quote validation, add trend scoring and configurable alerts.
