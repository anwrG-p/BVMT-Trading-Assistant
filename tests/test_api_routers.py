"""Tests for production FastAPI routers."""

import pytest
pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
from src.api.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_market_overview(client):
    response = client.get("/market/overview")
    assert response.status_code == 200
    data = response.json()
    assert "index" in data
    assert data["index"]["name"] == "TUNINDEX"
    assert "value" in data["index"]
    assert "gainers" in data
    assert isinstance(data["gainers"], list)
    assert len(data["gainers"]) > 0
    assert "losers" in data
    assert "sentiment" in data
    assert 0.0 <= data["sentiment"] <= 1.0
    assert "recent_alerts" in data

def test_stock_analysis(client):
    response = client.get("/stock/BIAT")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "BIAT"
    assert "price_history" in data
    assert len(data["price_history"]) > 0
    assert "indicators" in data
    assert "rsi" in data["indicators"]
    assert "recommendation" in data
    assert data["recommendation"]["action"] in ["ACHETER", "VENDRE", "CONSERVER"]

def test_portfolio(client):
    response = client.get("/portfolio")
    assert response.status_code == 200
    data = response.json()
    assert "capital" in data
    assert data["capital"] > 0
    assert "positions" in data
    assert len(data["positions"]) > 0
    assert "allocation" in data
    assert "performance" in data
    assert "suggestions" in data

def test_alerts(client):
    response = client.get("/alerts")
    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data
    assert len(data["alerts"]) > 0
    assert "filters" in data
    assert "Volume" in data["filters"]

def test_chat(client):
    response = client.post("/chat", json={"message": "Que pensez-vous de BIAT ?"})
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "BIAT" in data["reply"]
    assert "timestamp" in data
