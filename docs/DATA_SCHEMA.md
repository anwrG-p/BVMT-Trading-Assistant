# Data Schema Documentation

## 1. Input Data (`data/raw/`)

### 1.1 Cotations (Price Data)

**File Format:** CSV or TXT
**Naming Convention:** `cotation_YYYY.csv`

| Column                            | Type                           | Required | Description              | Example                                   |
| --------------------------------- | ------------------------------ | -------- | ------------------------ | ----------------------------------------- |
| `date` / `SEANCE`                 | String (YYYY-MM-DD/DD-MM-YYYY) | Yes      | Trading session date     | 2024-02-08                                |
| `symbol` / `CODE`                 | String                         | Yes      | Stock symbol             | SFBT                                      |
| `name` / `VALEUR`                 | String                         | Yes      | Company name             | STE DE FABRICATION DE BOISSONS DE TUNISIE |
| `open` / `OUVERTURE`              | Float                          | Yes      | Opening price (TND)      | 14.50                                     |
| `close` / `CLOTURE`               | Float                          | Yes      | Closing price (TND)      | 14.65                                     |
| `high` / `PLUS_HAUT`              | Float                          | Yes      | Daily high (TND)         | 14.70                                     |
| `low` / `PLUS_BAS`                | Float                          | Yes      | Daily low (TND)          | 14.45                                     |
| `volume` / `QUANTITE_NEGOCIEE`    | Integer                        | Yes      | Total shares traded      | 15430                                     |
| `transactions` / `NB_TRANSACTION` | Integer                        | No       | Count of trades          | 120                                       |
| `turnover` / `CAPITAUX`           | Float                          | No       | Total value traded (TND) | 225000.5                                  |

### 1.2 Dividends

**File Format:** Excel (`.xls`, `.xlsx`)
**Naming Convention:** `Dividendes_*.xlsx`

| Column                | Type     | Required | Description                      | Example    |
| --------------------- | -------- | -------- | -------------------------------- | ---------- |
| `Valeur` / `CODE`     | String   | Yes      | Stock symbol                     | SFBT       |
| `Date de détachement` | Datetime | Yes      | Ex-dividend date                 | 2023-06-15 |
| `Montant`             | Float    | Yes      | Dividend payment per share (TND) | 0.850      |

---

## 2. Processed Data (`data/processed/`)

### 2.1 Feature Matrix (`features.parquet`)

**Format:** Parquet

| Column                         | Type     | Description                           |
| ------------------------------ | -------- | ------------------------------------- |
| `date`                         | Datetime | Index column                          |
| `symbol`                       | Category | Stock symbol                          |
| `group`                        | Category | Stock group (11, 12, etc.)            |
| `open`, `high`, `low`, `close` | Float    | Adjusted price data                   |
| `volume`                       | Integer  | Raw volume                            |
| `log_return`                   | Float    | Logarithmic daily return (Target)     |
| `sma_20`, `sma_50`             | Float    | Simple Moving Averages                |
| `rsi_14`                       | Float    | Relative Strength Index (0-100)       |
| `macd`                         | Float    | Moving Average Convergence Divergence |
| `bb_upper`, `bb_lower`         | Float    | Bollinger Bands                       |
| `volatility_20`                | Float    | Rolling standard deviation of returns |
| `liquidity_regime`             | Integer  | 0=Low, 1=Normal, 2=High               |
| `is_ramadan`                   | Short    | 1 if date falls in Ramadan, else 0    |
| `day_of_week`                  | Short    | 0=Monday, 4=Friday                    |

---

## 3. Output Data (API Response)

### 3.1 Prediction Object

Structure of the JSON response from `/predict`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "symbol": { "type": "string" },
    "current_price": { "type": "number" },
    "current_date": { "type": "string", "format": "date" },
    "predictions": {
      "type": "object",
      "properties": {
        "price": {
          "type": "object",
          "patternProperties": {
            "^[1-5]$": {
              "type": "object",
              "properties": {
                "median": {
                  "type": "number",
                  "description": "Log return forecast"
                },
                "ci_95": {
                  "type": "object",
                  "properties": {
                    "lower": { "type": "number" },
                    "upper": { "type": "number" }
                  }
                }
              }
            }
          }
        },
        "volume": {
          "type": "object",
          "patternProperties": {
            "^[1-5]$": {
              "type": "object",
              "properties": {
                "volume": { "type": "number" },
                "liquidity_regime": {
                  "type": "string",
                  "enum": ["Low", "Normal", "High"]
                }
              }
            }
          }
        }
      }
    }
  }
}
```
