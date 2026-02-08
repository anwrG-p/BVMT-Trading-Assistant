# BVMT Trading Assistant 🇹🇳

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-beta-orange)

**An Intelligent Stock Price Forecasting System for the Tunisian Stock Market (BVMT).**

The **BVMT Trading Assistant** is a quantitative finance tool designed to forecast stock prices on the Tunisian Stock Exchange. It leverages advanced machine learning (XGBoost) to predict future price movements, estimate confidence intervals, and classify liquidity regimes. Built with a modern tech stack including FastAPI, Streamlit, and Docker, it offers a robust platform for local investors and analysts.

![Dashboard Demo](docs/assets/dashboard_screenshot.png) _(Placeholder for screenshot)_

## Key Features

- **Multi-Horizon Forecasting**: Predicts stock price movements for 1 to 5 days into the future.
- **Confidence Intervals**: Provides 80% and 95% confidence bands to quantify prediction uncertainty.
- **Volume & Liquidity Analysis**: Forecasts trading volume and classifies liquidity regimes (Low, Normal, High).
- **Dividend-Adjusted Data**: Automatically adjusts historical prices for dividend payouts to ensure accurate modeling.
- **Tunisian Market Context**: Integrates specific calendar features like Ramadan and BVMT trading holidays.
- **Interactive Dashboard**: A user-friendly Streamlit interface for visualizing forecasts and analyzing model performance.
- **Production-Ready API**: A FastAPI backend serving predictions and metrics via REST endpoints.
- **Dockerized Deployment**: Fully containerized application for easy setup and reproducibility.

## Table of Contents

- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Data Requirements](#data-requirements)
- [Model Performance](#model-performance)
- [Development](#development)
- [Deployment](#deployment)
- [Roadmap](#roadmap)
- [License](#license)

## Quick Start

### Prerequisites

- Docker & Docker Compose
- **OR** Python 3.9+ and Git

### Run with Docker (Recommended)

Get the system running in minutes:

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/BVMT-Trading-Assistant.git
cd BVMT-Trading-Assistant

# 2. Build and start services
docker-compose up -d --build

# 3. Access the dashboard
# Open http://localhost:8501 in your browser
```

### Expected Output

- **Dashboard**: `http://localhost:8501` - Interactive UI.
- **API Docs**: `http://localhost:8000/docs` - Swagger UI for the backend API.

## Architecture

The system follows a modular microservices-like architecture:

```mermaid
graph TD
    Data[Raw Data (CSV/Excel)] --> Ingestion[Data Ingestion Pipeline]
    Ingestion --> Features[Feature Engineering]
    Features --> Training[Model Training (XGBoost)]
    Training --> Models[Serialized Models]

    Models --> API[FastAPI Backend]
    Features --> API

    API --> Dashboard[Streamlit Dashboard]
    User((User)) --> Dashboard
```

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for a deep dive.

## Installation (Local Dev)

If you prefer running without Docker:

1.  **Clone and Setup Environment**

    ```bash
    git clone https://github.com/yourusername/BVMT-Trading-Assistant.git
    cd BVMT-Trading-Assistant
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

2.  **Run the API**

    ```bash
    uvicorn src.api.main:app --reload
    ```

3.  **Run the Dashboard**
    ```bash
    streamlit run src/dashboard/app.py
    ```

## Usage

### Using the Dashboard

1.  Navigate to `http://localhost:8501`.
2.  Select a stock symbol from the sidebar (e.g., `100010`, `SFBT`).
3.  Click **"Generate Forecast"**.
4.  View the **Price Forecast** chart with confidence intervals and the **Volume/Liquidity** analysis.
5.  Explore the **Model Performance** and **Feature Importance** tabs.

### Using the API

Make a prediction for a stock via curl:

```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"symbol": "SFBT", "horizons": [1, 5]}'
```

See [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) for full details.

## Data Requirements

The system expects data in the `data/raw` directory with the following structure:

- **Cotations**: Daily price data (CSV/TXT).
- **Dividends**: History of dividend payouts (Excel).

See [DATA_SCHEMA.md](docs/DATA_SCHEMA.md) for column specifications.

## Model Performance

The models are evaluated using Walk-Forward Validation. Key metrics include:

- **RMSE**: Root Mean Squared Error of price predictions.
- **Directional Accuracy**: Percentage of correct trend predictions.
- **Coverage**: Percentage of actual prices falling within confidence intervals.

Detailed benchmarks are available in [MODEL_CARD.md](docs/MODEL_CARD.md).

## Development

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Project Structure

- `src/api`: FastAPI backend.
- `src/dashboard`: Streamlit frontend.
- `src/models`: Forecasting models (XGBoost).
- `src/features`: Feature engineering logic.
- `src/data`: Data loaders and validators.
- `tests/`: Unit and integration tests.

See [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) for more info.

## Deployment

The application is containerized for easy deployment to cloud platforms (AWS, Azure, GCP) or on-premise servers.

See [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for production setup.

## Roadmap

- [ ] Integration with real-time market data feed.
- [ ] Portfolio optimization features.
- [ ] User authentication and personalized watchlists.
- [ ] Sentiment analysis from financial news.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, please open an issue on GitHub.
