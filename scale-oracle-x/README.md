# Scale Oracle X — Foundation V1

A free-first, AI-focused equity research and risk-control foundation.

## Implemented in this scaffold
- FastAPI backend health and watchlist endpoints.
- Starter watchlist loaded from the existing Global AI Stocks JSON.
- Transparent heuristic ranking from supplied price/volume metrics (not an ML prediction).
- Risk calculator for hypothetical paper-trade sizing; no broker connection or order execution.
- SQLite schema for future users, watchlists, signals, trades, portfolios, and model metadata.

## Not implemented yet
Authentication, live quote provider, news/sentiment ingestion, trained prediction model, background scanner, alerts, production database, broker integration, deployment, monitoring, and backups.

## Run on Windows (Python installed)
From this folder:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r backend\requirements.txt
py -m uvicorn backend.api.main:app --reload
```
Open http://127.0.0.1:8000/docs and http://127.0.0.1:8000/health.

The app reads `../data/global-ai-watchlist-v1.json` relative to this repository layout when available. If missing, it uses an empty list. Start the server from the repository root so paths resolve.

## Safety and data policy
- No real orders are placed.
- No market prices are fabricated.
- Ranking inputs are supplied by the caller; missing data is reported as unavailable.
- This is a local development scaffold, not a production-secure financial application.
- Do not put API keys, passwords, or broker credentials in source control.
