# 02: FastAPI Production Routers

**What to build:** Implement dedicated FastAPI endpoints for the React frontend (`/market/overview`, `/stock/{symbol}`, `/portfolio`, `/alerts`) backed by real historical features, technical indicators, and XGBoost predictors with robust fallback data.

**Blocked by:** None (can start immediately)

**Status:** resolved

- [x] Create Pydantic response models for market overview, stock analysis, portfolio summary, and alerts matching the frontend contracts
- [x] Implement `GET /market/overview` with real Tunindex computation, top gainers, top losers, and market sentiment
- [x] Implement `GET /stock/{symbol}` with historical price series, forecast horizon points, RSI/MACD indicators, and recommendation
- [x] Implement `GET /portfolio` with capital, positions, sector allocation, and rebalancing suggestions
- [x] Implement `GET /alerts` with active market anomaly and volatility notifications
- [x] Register all routers in `src/api/main.py`
- [x] Add comprehensive test suite in `tests/test_api_routers.py` verifying all routes
