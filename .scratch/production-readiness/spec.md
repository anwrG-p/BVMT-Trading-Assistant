# Production Readiness & Frontend Integration Spec

**Status:** ready-for-agent

## Problem Statement

The BVMT Trading Assistant has trained forecasting models and data pipelines, but lacks a complete production-grade deployment setup:
1. The modern React dashboard was left running on client-side mocks with JavaScript/JSX without TypeScript type guarantees, and its requested endpoints (`/market/overview`, `/stock/{symbol}`, `/portfolio`, `/alerts`) were missing from the FastAPI backend.
2. The `docker-compose.yml` only containerized the backend and Streamlit dashboard, omitting the React frontend.
3. Dead code, duplicate mock folders (`src/mock/` vs `src/mocks/`), and leftover debug files cluttered the repository.

## Solution

1. Implement dedicated FastAPI endpoints for Market Overview, Stock Analysis, Portfolio, and Alerts using the processed BVMT dataset and analytical models, with resilient fallback data.
2. Migrate `dashboard-frontend` to strict TypeScript (`.tsx`/`.ts`), typed API contracts, and verified Vite build.
3. Containerize `dashboard-frontend` via a production multi-stage Docker build with Nginx on port 3000 and reverse-proxying `/api` requests to FastAPI.
4. Clean up duplicate mock services, dead imports, and root debug artifacts.

## User Stories

1. As a trader, I want to access a unified React dashboard on port 3000, so that I can monitor the Tunisian market in real-time.
2. As a trader, I want to see Tunindex performance, top gainers, and top losers on the Market Overview page, so that I understand current market breadth.
3. As a quantitative analyst, I want to view XGBoost price forecasts alongside historical stock prices and technical indicators (RSI, MACD), so that I can evaluate stock trends.
4. As an investor, I want to inspect portfolio allocations and AI-driven rebalancing recommendations, so that I can optimize my risk-adjusted returns.
5. As a trader, I want to receive market and volatility alerts, so that I am notified of abnormal trading movements.
6. As a researcher, I want Streamlit retained on port 8501, so that I can inspect model internals and backtest distributions.
7. As a DevOps engineer, I want all services orchestratable via `docker-compose up`, so that deployment is reproducible and reliable.
8. As a frontend engineer, I want strict TypeScript types across the dashboard, so that UI contracts and API payloads are verified at build time.

## Implementation Decisions

- **FastAPI Endpoints**: Implement routers for `/market`, `/stock`, `/portfolio`, and `/alerts` conforming to the frontend data contracts.
- **Data Integration**: Connect endpoints to historical features (`features.parquet`), technical indicators, XGBoost predictions, and portfolio optimization.
- **TypeScript**: Configure `tsconfig.json`, add `typescript` and type dependencies, convert all `.jsx`/`.js` files under `dashboard-frontend/src` to `.tsx`/`.ts`.
- **Nginx & Docker**: Multi-stage build (Node builder -> Alpine Nginx) serving SPA with client-side routing fallback and API proxying.
- **Repo Hygiene**: Delete duplicate mock services, unused files, and scratch debug outputs.

## Testing Decisions

- **Backend API Tests**: Test FastAPI endpoints using `TestClient` for valid 200 responses, schema conformance, and error handling.
- **Frontend Type Safety**: Run `tsc --noEmit` and `vite build` ensuring zero TypeScript or packaging errors.
- **Docker Validation**: Validate Docker Compose specification.

## Out of Scope

- External production relational database hosting (e.g. cloud PostgreSQL setup) or live paid SMS alert gateways.
- Scraping external news websites during test execution.

## Further Notes

All changes maintain backward compatibility with existing Streamlit analytics and model validation scripts.
