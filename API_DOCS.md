# BVMT Trading Assistant API Documentation

## Base URL

`http://localhost:8000`

## Endpoints

### Health Check

**GET** `/health`
Check if the API and models are ready.

- **Response**:
  ```json
  {
    "status": "healthy",
    "models_loaded": true,
    "data_loaded": true
  }
  ```

### List Symbols

**GET** `/symbols`
Get list of available stock symbols.

- **Response**:
  ```json
  {
    "symbols": ["AB", "AD", "AF", ...],
    "count": 80
  }
  ```

### Predict (Single Stock)

**POST** `/predict`
Get forecasts for a specific stock.

- **Request Body**:
  ```json
  {
    "symbol": "SFBT",
    "horizons": [1, 2, 3, 4, 5]
  }
  ```
- **Response**:
  ```json
  {
    "symbol": "SFBT",
    "name": "STE FRIGORIFIQUE ET BRASSERIE DE TUNIS",
    "current_price": 14.50,
    "current_date": "2025-01-31",
    "predictions": {
      "price": {
        "1": {
          "median": 14.55,
          "ci_80": {"lower": 14.40, "upper": 14.70},
          "ci_95": {"lower": 14.30, "upper": 14.80}
        },
        ...
      },
      "volume": {
        "1": {
          "volume": 12500,
          "liquidity_regime": "High"
        },
        ...
      }
    }
  }
  ```

### Batch Prediction

**POST** `/predict/batch`
Get forecasts for multiple stocks.

- **Request Body**:
  ```json
  {
    "symbols": ["SFBT", "BIAT", "BT"],
    "horizons": [1]
  }
  ```
