-- Scale Oracle X starter schema (SQLite-compatible).
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS watchlists (
  id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS watchlist_symbols (
  watchlist_id TEXT NOT NULL REFERENCES watchlists(id) ON DELETE CASCADE,
  symbol TEXT NOT NULL, exchange_code TEXT, category TEXT,
  PRIMARY KEY (watchlist_id, symbol, exchange_code)
);
CREATE TABLE IF NOT EXISTS signals (
  id TEXT PRIMARY KEY, symbol TEXT NOT NULL, signal_type TEXT NOT NULL,
  score REAL, source_timestamp TEXT, status TEXT NOT NULL DEFAULT 'research_only',
  metadata_json TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS trades (
  id TEXT PRIMARY KEY, user_id TEXT REFERENCES users(id) ON DELETE SET NULL,
  symbol TEXT NOT NULL, side TEXT NOT NULL CHECK(side IN ('buy','sell')),
  quantity REAL NOT NULL CHECK(quantity > 0), price REAL,
  mode TEXT NOT NULL CHECK(mode IN ('paper','live')),
  status TEXT NOT NULL DEFAULT 'simulated', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS portfolios (
  id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL, currency TEXT NOT NULL DEFAULT 'USD',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS portfolio_positions (
  portfolio_id TEXT NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
  symbol TEXT NOT NULL, quantity REAL NOT NULL DEFAULT 0, average_cost REAL,
  PRIMARY KEY (portfolio_id, symbol)
);
CREATE TABLE IF NOT EXISTS models (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, version TEXT NOT NULL,
  model_type TEXT NOT NULL, artifact_location TEXT, metrics_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
