"""Scale-Oracle-X local API. Static watchlist + persistent paper trading only."""
from pathlib import Path
import json
import sqlite3
from typing import Any, Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = ROOT.parent
WATCHLIST_PATH = REPO_ROOT / "data" / "global-ai-watchlist-v1.json"
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "scale_oracle_x.sqlite3"
INITIAL_PAPER_CASH = 1000.0
MAX_POSITION_PERCENT = 10.0
MAX_TRADE_RISK_PERCENT = 1.0

app = FastAPI(title="Scale-Oracle-X API", version="0.2.0",
              description="Local research and paper-trading foundation. No live quotes or broker orders.")

def connect_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db

def init_db():
    with connect_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS paper_account (
            id INTEGER PRIMARY KEY CHECK(id = 1),
            cash REAL NOT NULL,
            realized_pnl REAL NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS paper_positions (
            symbol TEXT PRIMARY KEY, quantity REAL NOT NULL CHECK(quantity > 0),
            average_cost REAL NOT NULL CHECK(average_cost > 0), stop_loss REAL,
            take_profit REAL, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS paper_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT NOT NULL,
            side TEXT NOT NULL CHECK(side IN ('buy','sell')), quantity REAL NOT NULL,
            reference_price REAL NOT NULL, status TEXT NOT NULL DEFAULT 'simulated_filled',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        INSERT OR IGNORE INTO paper_account(id, cash) VALUES (1, 1000.0);
        """)

@app.on_event("startup")
def startup():
    init_db()

def load_watchlist() -> list[dict[str, Any]]:
    if not WATCHLIST_PATH.exists():
        return []
    try:
        payload = json.loads(WATCHLIST_PATH.read_text(encoding="utf-8"))
        return [{**item, "category": category.get("label", category.get("id", "Uncategorized"))}
                for category in payload.get("categories", [])
                for item in category.get("tickers", [])]
    except (OSError, json.JSONDecodeError):
        return []

class RiskRequest(BaseModel):
    account_value: float = Field(gt=0, le=1_000_000_000)
    risk_percent: float = Field(gt=0, le=5, description="Percent of account equity; 1 means 1%")
    entry_price: float = Field(gt=0)
    stop_price: float = Field(gt=0)
    max_position_percent: float = Field(default=10, gt=0, le=100)

class PaperOrderRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=24)
    side: Literal["buy", "sell"]
    quantity: float = Field(gt=0, le=1_000_000)
    reference_price: float = Field(gt=0, le=10_000_000)
    stop_loss: float | None = Field(default=None, gt=0)
    take_profit: float | None = Field(default=None, gt=0)

@app.get("/health")
def health():
    return {"status": "ok", "service": "scale-oracle-x", "version": "0.2.0",
            "mode": "local-paper-trading", "live_quotes": False,
            "broker_connected": False, "real_orders_enabled": False}

@app.get("/api/watchlist")
def watchlist(q: str | None = None, category: str | None = None):
    rows = load_watchlist()
    if q:
        term = q.casefold().strip()
        rows = [r for r in rows if term in str(r.get("symbol", "")).casefold()
                or term in str(r.get("company", "")).casefold()
                or term in str(r.get("country", "")).casefold()]
    if category:
        rows = [r for r in rows if category.casefold() in str(r.get("category", "")).casefold()]
    return {"count": len(rows), "data_status": "static watchlist; no live prices", "items": rows}

@app.post("/api/risk/position-size")
def position_size(req: RiskRequest):
    if req.entry_price == req.stop_price:
        raise HTTPException(status_code=422, detail="Entry and stop prices must differ.")
    risk_budget = req.account_value * req.risk_percent / 100
    per_share_risk = abs(req.entry_price - req.stop_price)
    risk_shares = int(risk_budget // per_share_risk)
    cap_dollars = req.account_value * req.max_position_percent / 100
    cap_shares = int(cap_dollars // req.entry_price)
    shares = max(0, min(risk_shares, cap_shares))
    return {"mode": "hypothetical_only", "shares": shares,
            "estimated_position_value": round(shares * req.entry_price, 2),
            "estimated_loss_at_stop": round(shares * per_share_risk, 2),
            "risk_budget": round(risk_budget, 2),
            "position_cap_dollars": round(cap_dollars, 2),
            "warning": "Illustrative sizing only. Stop fills are not guaranteed; fees, slippage, gaps and taxes are excluded."}

@app.get("/api/paper/account")
def paper_account():
    with connect_db() as db:
        account = db.execute("SELECT cash, realized_pnl FROM paper_account WHERE id=1").fetchone()
        positions = db.execute("SELECT symbol, quantity, average_cost, stop_loss, take_profit FROM paper_positions ORDER BY symbol").fetchall()
        return {"mode": "paper_only", "initial_cash": INITIAL_PAPER_CASH,
                "cash": round(account["cash"], 2), "realized_pnl": round(account["realized_pnl"], 2),
                "positions": [dict(p) for p in positions],
                "pricing_note": "Positions use recorded reference prices; no live market valuation is available."}

@app.post("/api/paper/orders")
def paper_order(req: PaperOrderRequest):
    symbol = req.symbol.strip().upper()
    allowed = {row["symbol"].upper() for row in load_watchlist()}
    if symbol not in allowed:
        raise HTTPException(status_code=400, detail="Symbol is not in the configured AI-related watchlist.")
    if req.side == "buy":
        if req.stop_loss is None or req.take_profit is None:
            raise HTTPException(status_code=422, detail="Paper BUY requires both stop_loss and take_profit.")
        if not (req.stop_loss < req.reference_price < req.take_profit):
            raise HTTPException(status_code=422, detail="For a long position, stop_loss < reference_price < take_profit is required.")
        notional = req.quantity * req.reference_price
        with connect_db() as db:
            db.execute("BEGIN IMMEDIATE")
            account = db.execute("SELECT cash FROM paper_account WHERE id=1").fetchone()
            existing = db.execute("SELECT quantity FROM paper_positions WHERE symbol=?", (symbol,)).fetchone()
            if notional > INITIAL_PAPER_CASH * MAX_POSITION_PERCENT / 100:
                raise HTTPException(status_code=400, detail="Order exceeds the 10% initial-account position cap.")
            trade_risk = req.quantity * (req.reference_price - req.stop_loss)
            if trade_risk > INITIAL_PAPER_CASH * MAX_TRADE_RISK_PERCENT / 100:
                raise HTTPException(status_code=400, detail="Order exceeds the 1% initial-account stop-risk cap.")
            if existing:
                raise HTTPException(status_code=400, detail="V1 allows one entry per symbol; close the position before reopening.")
            if notional > account["cash"]:
                raise HTTPException(status_code=400, detail="Insufficient paper cash.")
            db.execute("UPDATE paper_account SET cash=cash-? WHERE id=1", (notional,))
            db.execute("INSERT INTO paper_positions(symbol,quantity,average_cost,stop_loss,take_profit) VALUES(?,?,?,?,?)",
                       (symbol, req.quantity, req.reference_price, req.stop_loss, req.take_profit))
            cur = db.execute("INSERT INTO paper_orders(symbol,side,quantity,reference_price) VALUES(?,?,?,?)",
                             (symbol, "buy", req.quantity, req.reference_price))
            return {"status": "simulated_filled", "order_id": cur.lastrowid, "symbol": symbol,
                    "side": "buy", "quantity": req.quantity, "reference_price": req.reference_price,
                    "notional": round(notional, 2), "mode": "paper_only"}
    with connect_db() as db:
        db.execute("BEGIN IMMEDIATE")
        position = db.execute("SELECT quantity, average_cost FROM paper_positions WHERE symbol=?", (symbol,)).fetchone()
        if not position or req.quantity > position["quantity"]:
            raise HTTPException(status_code=400, detail="Cannot sell more shares than the existing paper position.")
        proceeds = req.quantity * req.reference_price
        pnl = req.quantity * (req.reference_price - position["average_cost"])
        remaining = position["quantity"] - req.quantity
        db.execute("UPDATE paper_account SET cash=cash+?, realized_pnl=realized_pnl+? WHERE id=1", (proceeds, pnl))
        if remaining <= 1e-9:
            db.execute("DELETE FROM paper_positions WHERE symbol=?", (symbol,))
        else:
            db.execute("UPDATE paper_positions SET quantity=?, updated_at=CURRENT_TIMESTAMP WHERE symbol=?", (remaining, symbol))
        cur = db.execute("INSERT INTO paper_orders(symbol,side,quantity,reference_price) VALUES(?,?,?,?)",
                         (symbol, "sell", req.quantity, req.reference_price))
        return {"status": "simulated_filled", "order_id": cur.lastrowid, "symbol": symbol,
                "side": "sell", "quantity": req.quantity, "reference_price": req.reference_price,
                "realized_pnl": round(pnl, 2), "mode": "paper_only"}

@app.get("/api/paper/orders")
def paper_orders():
    with connect_db() as db:
        rows = db.execute("SELECT id,symbol,side,quantity,reference_price,status,created_at FROM paper_orders ORDER BY id DESC LIMIT 100").fetchall()
        return {"mode": "paper_only", "items": [dict(row) for row in rows]}
