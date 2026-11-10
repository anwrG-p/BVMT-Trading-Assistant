# API Documentation

## Base URL

`http://localhost:8000`

## Endpoints

### 1. `POST /predict`

**Purpose:** Generate forecast for a single stock.

**Request:**

```json
{
  "symbol": "SFBT",
  "horizons": [1, 2, 3, 4, 5]
}
```

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| symbol | string | Yes | - | Stock symbol (e.g., "SFBT", "BIAT") |
| horizons | list[int] | No | [1, 2, 3, 4, 5] | Prediction horizons (days) |

**Response:**

```json
{
  "symbol": "SFBT",
  "current_price": 14.50,
  "current_date": "2024-02-08",
  "predictions": {
    "price": {
      "1": {
        "median": 0.012,
        "ci_95": {"lower": -0.02, "upper": 0.04},
        "ci_80": {"lower": -0.01, "upper": 0.03}
      },
      ...
    },
    "volume": {
      "1": {
        "volume": 15000,
        "liquidity_regime": "Normal"
      },
      ...
    }
  }
}
```

**Error Codes:**

- 404: `Symbol not found`
- 503: `Service not ready` (model/data not loaded)

---

### 2. `GET /visualization/{symbol}`

**Purpose:** Get full history and forecast data for charting.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| symbol | string | Yes | - | Stock symbol |
| horizons | string | No | "1,2,3,4,5" | Comma-separated list of horizons |

**Response:**

```json
{
  "symbol": "SFBT",
  "data": [
    {
      "date": "2024-01-01",
      "price": 14.20,
      "type": "history",
      "lower_bound": null,
      "upper_bound": null
    },
    ...
    {
      "date": "2024-02-09",
      "price": 14.65,
      "type": "forecast",
      "lower_bound": 14.40,
      "upper_bound": 14.90
    }
  ]
}
```

---

### 3. `GET /metrics`

**Purpose:** Get model performance metrics and feature importance.

**Response:**

```json
{
  "price_metrics": [
    {
      "horizon": 1,
      "rmse": 0.45,
      "mae": 0.32,
      "directional_accuracy": 0.65
    },
    ...
  ],
  "backtest_metrics": {
    "total_return": 0.12,
    "win_rate": 0.58,
    "sharpe_ratio": 1.2
  },
  "feature_importance": [
    {"feature": "rsi_14", "importance": 0.15},
    {"feature": "ema_20", "importance": 0.12},
    ...
  ]
}
```

---

### 4. `POST /predict/realtime`

**Purpose:** Trigger real-time data fetch and prediction.

**Request:**

```json
{
  "symbol": "SFBT",
  "horizons": [1, 5]
}
```

**Response:** Same structure as `POST /predict`.

---

### 5. `GET /health`

**Purpose:** Check service health.

**Response:**

```json
{
  "status": "healthy",
  "models_loaded": true,
  "data_loaded": true
}
```

---

### 6. `GET /market/overview`

**Purpose:** Get full market overview with TUNINDEX index performance, top gainers, losers, sentiment, and recent alerts.

**Response:**

```json
{
  "index": {
    "name": "TUNINDEX",
    "value": 13449.95,
    "change": 0.62
  },
  "gainers": [
    { "symbol": "BIAT", "price": 94.50, "change": 2.45 },
    { "symbol": "ATTIJARI BANK", "price": 52.10, "change": 1.85 }
  ],
  "losers": [
    { "symbol": "UIB", "price": 24.20, "change": -1.82 },
    { "symbol": "STAR", "price": 165.00, "change": -1.49 }
  ],
  "sentiment": 0.68,
  "recent_alerts": [
    {
      "id": 1,
      "symbol": "BIAT",
      "type": "volume",
      "description": "Volume record sur BIAT",
      "timestamp": "10:30"
    }
  ],
  "marketVolume": 1845000.0,
  "activeTraders": 1240
}
```

---

### 7. `GET /stock/{symbol}`

**Purpose:** Get 60-day historical close price series, 5-day predictive forecasts, RSI (14), MACD signals, and recommendation.

**Response:**

```json
{
  "symbol": "BIAT",
  "name": "BIAT - Bourse de Tunis",
  "price_history": [
    { "date": "2025-01-02", "value": 93.9, "forecast": false },
    { "date": "2025-01-09", "value": 95.8, "forecast": true }
  ],
  "sentiment_timeline": [
    { "date": "2025-01-02", "score": 0.72 }
  ],
  "indicators": {
    "rsi": 58.4,
    "macd": "Croisement Haussier (Bullish Crossover)"
  },
  "recommendation": {
    "action": "ACHETER",
    "confidence": 84.0
  }
}
```

---

### 8. `GET /portfolio`

**Purpose:** Get user portfolio metrics, positions, sector allocation, performance timeline, and AI optimization suggestions.

**Response:**

```json
{
  "capital": 93226.0,
  "roi": 12.4,
  "positions": [
    { "symbol": "BIAT", "quantity": 250, "buyPrice": 90.0, "currentPrice": 94.5, "pl": 1125.0 }
  ],
  "allocation": [
    { "name": "Secteur Bancaire", "value": 58.0 },
    { "name": "Biens de Consommation", "value": 22.0 }
  ],
  "performance": [
    { "date": "2025-02", "value": 93226.0 }
  ],
  "suggestions": [
    "Surpondération sur le secteur bancaire. Rééquilibrer vers l'agroalimentaire."
  ]
}
```

---

### 9. `GET /alerts`

**Purpose:** Get active real-time anomaly, volume, and price alerts with severity classifications.

**Response:**

```json
{
  "alerts": [
    {
      "id": 1,
      "symbol": "BIAT",
      "type": "Volume",
      "severity": "High",
      "timestamp": "10:30",
      "status": "Open"
    }
  ],
  "filters": ["All", "Volume", "Price", "News", "Market"]
}
```

---

### 10. `POST /chat`

**Purpose:** Trading assistant interactive question/answering endpoint.

**Request:**

```json
{
  "message": "Quelle est la tendance sur BIAT ?"
}
```

**Response:**

```json
{
  "reply": "BIAT affiche une dynamique haussière avec une rentabilité solide...",
  "timestamp": "10:35"
}
```
