# Scale-Oracle-X implementation status

## In repository
- Static global AI-related equity watchlist source.
- FastAPI health, watchlist, hypothetical risk-sizing, paper-account, paper-order, and paper-order-history routes.
- SQLite-backed paper account, positions, and simulated order ledger.
- V1 guardrails: configured watchlist symbols only, long-only, mandatory stop/target on entries, 10% initial-account position cap, 1% initial-account stop-risk cap.
- Transparent heuristic ranking module and starter relational schema.

## Not yet implemented
Authentication/authorization, live quotes, historical data pipeline, timestamped data validation, news/sentiment ingestion, trained ML, backtesting, background scanner, automatic stop/target execution, browser UI integration, broker integration, production deployment, monitoring and backups.

## Verification
Repository changes are committed. Runtime tests have not yet been executed on the user's Windows computer. Paper orders use caller-supplied reference prices and are not market executions. Keep the unauthenticated API on localhost.
