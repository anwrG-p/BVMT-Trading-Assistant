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
