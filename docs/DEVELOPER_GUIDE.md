# Developer Guide

## Setup Development Environment

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/BVMT-Trading-Assistant.git
cd BVMT-Trading-Assistant
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install Dev Dependencies

```bash
pip install -r requirements.txt
pip install pytest black isort
```

## Project Structure

```bash
bvmt-forecaster/
├── src/
│   ├── api/                # FastAPI backend
│   │   ├── main.py
│   │   ├── predictor.py
│   │   └── schemas/
│   ├── dashboard/          # Streamlit frontend
│   │   └── app.py
│   ├── data/               # Data loaders, validators
│   │   ├── loader.py
│   │   ├── catalog.py
│   │   └── validation/
│   ├── features/           # Feature engineering
│   │   ├── engine.py
│   │   └── generators/
│   ├── models/             # Forecasting models
│   │   ├── base.py
│   │   ├── trainer.py
│   │   ├── price_forecaster.py
│   │   └── volume_forecaster.py
│   ├── utils/              # Logging, config
│   │   ├── logger.py
│   │   └── config.py
│   └── modules/            # Misc modules
├── tests/                  # Unit tests
├── config/                 # Config files
├── docker/                 # Dockerfiles
├── notebooks/              # Jupyter notebooks
└── docs/                   # Documentation
```

## Adding New Features

### Example: Adding a New Technical Indicator

1.  **Define Logic**: Open `src/features/generators/price_features.py` (or create a new generator).
2.  **Implement Function**: Add a function that takes a DataFrame and returns the indicator column.
    ```python
    def calculate_bollinger_bands(df, window=20):
        # Implementation...
        return df
    ```
3.  **Register Feature**: Add the feature to `src/features/engine.py` pipeline.
4.  **Update Config**: Add column name to `config/config.yaml` feature list.

## Adding New Models

### 1. Create Model Class

Inherit from `BaseForecaster` in `src/models/base.py`.

```python
class MyNewModel(BaseForecaster):
    def fit(self, X, y):
        # Fitting logic
        pass

    def predict(self, X):
        # Prediction logic
        return pred
```

### 2. Register Model

Update `src/models/trainer.py` to recognize the new model type in configuration.

## Testing Strategy

- `pytest` for all unit tests.
- `scripts/verify_api.py` for integration testing.

```bash
pytest tests/
python scripts/verify_api.py
```

## Code Style

- **Conventions**: PEP 8.
- **Formatter**: Black.
- **Imports**: Isort.
- **Docstrings**: Google Style.

## Git Workflow

1.  Create a feature branch: `git checkout -b feature/new-indicator`.
2.  Commit changes: `git commit -m "feat: add bollinger bands"`.
3.  Push: `git push origin feature/new-indicator`.
4.  Open Pull Request.
