# Scale-Oracle-X — Integrated Foundation V1

A local, free-first AI-equity research and paper-trading foundation.

## What V1 currently contains
- FastAPI health, static AI watchlist, hypothetical position-sizing, paper-account, paper-order, and order-history routes.
- Persistent SQLite paper account, positions, and simulated order ledger.
- Paper BUY/SELL restricted to symbols in the configured AI watchlist.
- V1 guardrails: maximum 10% of the initial $1,000 account per position and maximum 1% of initial account value at the stop per new position.
- BUY requires a stop-loss and take-profit; short selling and real broker orders are not supported.
- Transparent heuristic ranking function (not a trained ML model) and starter relational schema.

## Windows setup
Open PowerShell and run these commands from the repository's `scale-oracle-x` folder:

```powershell
cd path\to\personal-stocks-market\scale-oracle-x
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r backend\requirements.txt
py -m pytest tests\npy -m uvicorn backend.api.main:app --reload
```

Then open http://127.0.0.1:8000/health and http://127.0.0.1:8000/docs.

The SQLite database is created at `scale-oracle-x/data/scale_oracle_x.sqlite3`. The API reads the starter universe from the repository-level `data/global-ai-watchlist-v1.json`.

## Paper workflow
1. Read `GET /api/paper/account`.
2. Read symbols from `GET /api/watchlist`.
3. Calculate hypothetical size with `POST /api/risk/position-size`.
4. Submit a simulated BUY to `POST /api/paper/orders` with symbol, side, quantity, reference_price, stop_loss, and take_profit.
5. Close some or all shares with a simulated SELL.
6. Review `GET /api/paper/orders` and the account endpoint.

These endpoints use caller-supplied reference prices. They do not retrieve quotes, automatically trigger stop-loss/take-profit, or send orders to a broker. The $1,000 balance is simulated, not real funds.

## Not implemented / not verified
Authentication and authorization, live/historical market-data adapters, timestamped quote cache, news/sentiment feeds, trained prediction models, backtesting, automatic scanning/scheduling, automatic stop/target monitoring, browser dashboard integration, broker integration, deployment, monitoring, and backups remain future work. The code has not yet been run on the user's Windows computer.

## Safety
Keep this API bound to localhost during V1. It has no authentication. Do not expose it to the internet or store provider/broker secrets in source control. Paper fills are immediate reference-price simulations and do not model liquidity, partial fills, fees, slippage, halts, or gaps.
