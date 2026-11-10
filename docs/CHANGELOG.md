# Changelog

## [1.0.0] - 2024-02-08

### Added

- **API**: FastAPI endpoints for `/predict`, `/visualization/{symbol}`, `/metrics`, `/health`.
- **Dashboard**: Streamlit app with interactive charts (History + Forecast), CI visualization, and feature importance.
- **Models**: Multi-Horizon XGBoost Quantile Regressors (Price) and XGBoost Classifier (Volume/Liquidity).
- **Features**: Comprehensive feature engineering pipeline (Price, Volume, Market, Calendar).
- **Data**: Support for CSV/TXT Cotations and Excel Dividends.
- **Docker**: Full containerization (`Dockerfile`, `docker-compose.yml`).
- **Docs**: Complete documentation suite (`README.md`, `ARCHITECTURE.md`, `API_DOCUMENTATION.md`, etc.).

### Changed

- **Pipeline**: Refactored data ingestion to use Factory Pattern for loaders.
- **Validation**: Implemented Walk-Forward Validation for robust performance metrics.

### Deprecated

- Legacy scripts in `notebooks/` are now superseded by the `src/` modules.

### Removed

- Placeholder scripts from initial project setup.

### Fixed

- Addressed floating-point precision issues in quantile lookup for confidence intervals.
- Corrected volume forecasting logic for missing thresholds.
