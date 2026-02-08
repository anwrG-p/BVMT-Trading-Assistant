# System Architecture

## Overview

The BVMT Trading Assistant is designed as a modular, extensible system for financial time series forecasting. It follows a clean separation of concerns, ensuring maintainability and scalability.

```mermaid
graph TD
    subgraph Data Layer
        RawData[Raw Data (CSV/Excel)]
        Loaders[Data Loaders]
        Catalog[Data Catalog]
        RawData --> Loaders
        Loaders --> Catalog
    end

    subgraph Feature Layer
        Engine[Feature Pipeline]
        PriceFeat[Price Features]
        VolFeat[Volume Features]
        CalFeat[Calendar Features]

        Catalog --> Engine
        Engine --> PriceFeat
        Engine --> VolFeat
        Engine --> CalFeat
        PriceFeat --> ProcessedData[Feature Matrix]
        VolFeat --> ProcessedData
        CalFeat --> ProcessedData
    end

    subgraph Model Layer
        Trainer[Model Trainer]
        XGB_Price[XGBoost Price Models]
        XGB_Vol[XGBoost Volume Models]

        ProcessedData --> Trainer
        Trainer --> XGB_Price
        Trainer --> XGB_Vol
    end

    subgraph Service Layer
        API[FastAPI Service]
        Predictor[StockPredictor]

        XGB_Price --> Predictor
        XGB_Vol --> Predictor
        Predictor --> API
    end

    subgraph Presentation Layer
        Dashboard[Streamlit Dashboard]
        API --> Dashboard
    end
```

## Module Breakdown

### 1. Data Ingestion Pipeline (`src/data`)

- **Purpose**: Load and validate raw financial data.
- **Components**:
  - `BaseLoader`: Abstract base class for all loaders.
  - `CSVLoader`: Handles daily price cotations (2022-2025).
  - `TXTLoader`: Parses legacy text-based cotations (2012-2021).
  - `ExcelLoader`: Ingests dividend payout history.
  - `DividendAdjuster`: Adjusts historical prices for dividends to prevent artificial price drops.
- **Design Pattern**: Factory Pattern for selecting the correct loader based on file type.

### 2. Feature Engineering Engine (`src/features`)

- **Purpose**: Transform raw time series into predictive features.
- **Key Features**:
  - **Price**: SMA, EMA, RSI, MACD, Bollinger Bands.
  - **Volume**: Log-transformed volume, Liquidity Regimes (Quantile-based).
  - **Market**: Correlation with TUNINDEX (Market Beta).
  - **Calendar**: Day of week, Month, Ramadan seasonality.
- **Design Pattern**: Pipeline Pattern to chain feature transformers.

### 3. Model Training Pipeline (`src/models`)

- **Purpose**: Train and serialize forecasting models.
- **Models**:
  - **Price Forecaster**: Multi-horizon XGBoost Regressors (Day 1 to 5). Uses Quantile Regression to estimate uncertainty (80%, 95% Confidence Intervals).
  - **Volume Forecaster**: Classifies future liquidity into Low, Normal, High regimes.
- **Validation**: Walk-Forward Validation to simulate real-world performance.

### 4. Prediction Service (`src/api`)

- **Purpose**: Serve predictions via REST API.
- **Endpoints**:
  - `/predict`: Single stock forecast.
  - `/visualization/{symbol}`: Full history + forecast for charting.
  - `/metrics`: Model performance stats.
- **Technology**: FastAPI, Uvicorn.

### 5. Visualization Layer (`src/dashboard`)

- **Purpose**: User interface for investors.
- **Technology**: Streamlit, Plotly.
- **Features**: Interactive charts, metric cards, feature importance plots.

## Data Flow

1.  **Ingestion**: Raw files -> `src/data` -> `pandas.DataFrame`.
2.  **Processing**: Dividend Adjustment -> `src/features` -> Feature Matrix.
3.  **Training**: Feature Matrix -> `src/models` -> `.pkl` files.
4.  **Inference**: API Request -> `StockPredictor` -> Load Models -> Generate Prediction -> JSON Response.

## Technology Choices

| Component     | Technology    | Justification                                                                               |
| ------------- | ------------- | ------------------------------------------------------------------------------------------- |
| **Language**  | Python 3.9+   | Standard for Data Science/ML.                                                               |
| **Data**      | Pandas, Numpy | Efficient in-memory data manipulation.                                                      |
| **ML**        | XGBoost       | High performance on tabular time-series data; supports missing values and interpretability. |
| **API**       | FastAPI       | High performance, auto-generated docs, type safety.                                         |
| **UI**        | Streamlit     | Rapid prototyping, native Python support, great for data apps.                              |
| **Container** | Docker        | Reproducibility, easy deployment.                                                           |

## Scalability Considerations

- **Horizontal Scaling**: The API is stateless and can be scaled horizontally using a load balancer (e.g., Nginx, AWS ALB) and multiple Docker containers.
- **Data Volume**: Currently uses in-memory processing. For larger datasets, migration to Dask or Spark would be required.
- **Model Storage**: Models are stored locally. For production, use an artifact store like S3 or MLflow.

## Security Measures

- **Input Validation**: Pydantic models ensure request data validity.
- **Error Handling**: Graceful error handling prevents information leakage via stack traces (in prod).
- **CORS**: Configured to allow specific origins.
