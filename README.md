# BVMT Trading Assistant 🇹🇳📈

A production-grade stock price forecasting system for the Tunisian Stock Exchange (BVMT).

## 🚀 Features

- **Multi-Horizon Forecasting**: Predicts stock prices 1-5 days ahead using XGBoost with Quantile Regression.
- **Confidence Intervals**: Provides 80% and 95% confidence intervals for risk management.
- **Liquidity Analysis**: Forecasts volume and classifies liquidity regimes (Low/Normal/High) using Q20/Q80 thresholds.
- **Tunisia-Specific**:
  - Ramadan calendar impact integration (via `hijri-converter`).
  - BVMT trading hours and holidays.
  - Dividend adjustments (custom engine).
- **Interactive Dashboard**: Streamlit app for visualizing predictions and model performance.
- **REST API**: FastAPI service for model inference.

## 🛠️ Architecture

```
BVMT-Trading-Assistant/
├── config/                 # Configuration (YAML)
├── data/                   # Data storage
│   ├── raw/                # Source files (BVMT quotations, dividends)
│   ├── processed/          # Parquet files
│   └── reports/            # Validation reports
├── models/                 # Saved models (XGBoost)
├── scripts/                # Utility scripts
├── src/                    # Source code
│   ├── api/                # FastAPI application
│   ├── dashboard/          # Streamlit dashboard
│   ├── data/               # Ingestion & Validation
│   ├── features/           # Feature Engineering
│   ├── models/             # Model definitions
│   ├── validation/         # Backtesting & Metrics
│   └── utils/              # Logging & Config
└── tests/                  # Unit & Integration tests
```

## 📦 Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/BVMT-Trading-Assistant.git
   cd BVMT-Trading-Assistant
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment** (optional):
   ```bash
   # Create .env file if needed
   cp .env.example .env
   ```

## 🚦 Usage Needs

### 1. Data Ingestion

Load raw data, apply dividend adjustments, and clean:

```bash
python scripts/ingest_data.py
```

### 2. Feature Engineering

Generate technical indicators (RSI, MACD, Bollinger Bands, etc.):

```bash
# This is handled automatically by the training pipeline,
# or can be run via:
python src/features/pipeline.py
```

### 3. Model Training & Validation

Train models validation/backtesting:

```bash
python scripts/validate_models.py
```

_Note: This script trains models using a walk-forward validation approach and saves performance metrics._

### 4. Run API

Start the prediction service:

```bash
uvicorn src.api.main:app --reload
```

Open `http://localhost:8000/docs` for API documentation.

### 5. Run Dashboard

Launch the visualization app:

```bash
streamlit run src/dashboard/app.py
```

## 📊 Performance Metrics

The system evaluates models using:

- **RMSE/MAE**: Accuracy of point forecasts.
- **Directional Accuracy**: Ability to predict price movement direction.
- **CI Coverage**: Verification of uncertainty estimates (target: 95%).
- **Sharpe Ratio**: Risk-adjusted returns in backtesting.

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

## 📝 License

MIT License. See [LICENSE](LICENSE) for details.
