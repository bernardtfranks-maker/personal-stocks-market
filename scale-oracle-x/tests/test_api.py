import json
from fastapi.testclient import TestClient
from backend.api import main

def test_health_and_watchlist(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "data" / "test.sqlite3")
    watchlist = tmp_path / "watchlist.json"
    watchlist.write_text(json.dumps({"categories":[{"id":"ai","label":"AI","tickers":[{"symbol":"NVDA","company":"NVIDIA","country":"US"}]}]}), encoding="utf-8")
    monkeypatch.setattr(main, "WATCHLIST_PATH", watchlist)
    with TestClient(main.app) as client:
        assert client.get("/health").json()["real_orders_enabled"] is False
        response = client.get("/api/watchlist")
        assert response.status_code == 200
        assert response.json()["items"][0]["symbol"] == "NVDA"

def test_paper_buy_sell_and_guardrails(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "data" / "test.sqlite3")
    watchlist = tmp_path / "watchlist.json"
    watchlist.write_text(json.dumps({"categories":[{"id":"ai","label":"AI","tickers":[{"symbol":"NVDA","company":"NVIDIA","country":"US"}]}]}), encoding="utf-8")
    monkeypatch.setattr(main, "WATCHLIST_PATH", watchlist)
    with TestClient(main.app) as client:
        before = client.get("/api/paper/account").json()
        assert before["cash"] == 1000.0
        buy = client.post("/api/paper/orders", json={
            "symbol":"NVDA","side":"buy","quantity":0.1,
            "reference_price":100,"stop_loss":95,"take_profit":110
        })
        assert buy.status_code == 200
        assert buy.json()["status"] == "simulated_filled"
        account = client.get("/api/paper/account").json()
        assert account["cash"] == 990.0
        assert len(account["positions"]) == 1
        sell = client.post("/api/paper/orders", json={
            "symbol":"NVDA","side":"sell","quantity":0.1,"reference_price":105
        })
        assert sell.status_code == 200
        assert sell.json()["realized_pnl"] == 0.5
        assert client.get("/api/paper/account").json()["positions"] == []

        too_risky = client.post("/api/paper/orders", json={
            "symbol":"NVDA","side":"buy","quantity":1,
            "reference_price":100,"stop_loss":90,"take_profit":120
        })
        assert too_risky.status_code == 400
