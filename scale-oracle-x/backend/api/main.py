"""Scale Oracle X local API foundation. No live trading or market-data claims."""
from pathlib import Path
import json
from typing import Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Scale Oracle X API", version="0.1.0",
              description="Local development foundation; not a broker or live quote service.")

ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = ROOT.parent
WATCHLIST_PATH = REPO_ROOT / "data" / "global-ai-watchlist-v1.json"

def load_watchlist() -> list[dict[str, Any]]:
    if not WATCHLIST_PATH.exists():
        return []
    try:
        payload = json.loads(WATCHLIST_PATH.read_text(encoding="utf-8"))
        rows = []
        for category in payload.get("categories", []):
            for item in category.get("tickers", []):
                rows.append({**item, "category": category.get("label", category.get("id", "Uncategorized"))})
        return rows
    except (OSError, json.JSONDecodeError):
        return []

class RiskRequest(BaseModel):
    account_value: float = Field(gt=0, le=1_000_000_000)
    risk_percent: float = Field(gt=0, le=1)
    entry_price: float = Field(gt=0)
    stop_price: float = Field(gt=0)
    max_position_percent: float = Field(default=10, gt=0, le=100)

@app.get("/health")
def health():
    return {"status": "ok", "service": "scale-oracle-x", "version": "0.1.0",
            "mode": "local-scaffold", "live_quotes": False, "broker_connected": False}

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
    """Hypothetical share sizing only; never submits orders."""
    if req.entry_price == req.stop_price:
        raise HTTPException(status_code=422, detail="Entry and stop prices must differ.")
    risk_budget = req.account_value * (req.risk_percent / 100)
    per_share_risk = abs(req.entry_price - req.stop_price)
    risk_limited_shares = int(risk_budget // per_share_risk)
    cap_dollars = req.account_value * req.max_position_percent / 100
    cap_shares = int(cap_dollars // req.entry_price)
    shares = max(0, min(risk_limited_shares, cap_shares))
    return {
        "mode": "hypothetical_only",
        "shares": shares,
        "estimated_position_value": round(shares * req.entry_price, 2),
        "estimated_loss_at_stop": round(shares * per_share_risk, 2),
        "risk_budget": round(risk_budget, 2),
        "position_cap_dollars": round(cap_dollars, 2),
        "warning": "Illustrative sizing only; assumes stop execution at the specified price and excludes fees, slippage, gaps, and taxes."
    }
