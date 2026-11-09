import pytest
pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
import pandas as pd
from datetime import datetime

from src.api.main import app
import src.api.main as main_module


@pytest.fixture
def client():
    # Setup dummy features_df for testing endpoints
    main_module.features_df = pd.DataFrame({
        'date': [datetime(2023, 1, 1), datetime(2023, 1, 2)],
        'symbol': ['SFBT', 'SFBT'],
        'name': ['SFBT', 'SFBT'],
        'close': [15.0, 15.5],
        'high': [15.2, 15.8],
        'low': [14.8, 15.1],
        'open': [14.9, 15.2],
        'volume': [5000, 6000],
        'rsi': [55.0, 60.0]
    })
    return TestClient(app)


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["data_loaded"] is True


def test_symbols_endpoint(client):
    response = client.get("/symbols")
    assert response.status_code == 200
    data = response.json()
    assert "symbols" in data
    assert "SFBT" in data["symbols"]


def test_predict_endpoint(client):
    response = client.post("/predict", json={"symbol": "SFBT", "horizons": [1, 2]})
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "SFBT"
    assert "predictions" in data


def test_visualization_endpoint(client):
    response = client.get("/visualization/SFBT")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "SFBT"
    assert "data" in data
