# 03: Frontend TypeScript Migration

**What to build:** Migrate `dashboard-frontend` from JavaScript/JSX to strictly typed TypeScript (.tsx/.ts) with typed API contracts, typed Auth context, and successful typechecking with zero build errors.

**Blocked by:** 01: Repo Cleanup and Prefactoring

**Status:** resolved

- [x] Install `typescript`, `@types/node`, and related dev dependencies in `dashboard-frontend`
- [x] Configure `tsconfig.json` and `tsconfig.node.json`
- [x] Create TypeScript API contracts in `dashboard-frontend/src/types/`
- [x] Convert `src/services/api.js` and `src/mocks/*` to TypeScript
- [x] Convert `src/auth/*` and `src/routes/*` to TypeScript
- [x] Convert all pages (`MarketOverview`, `StockAnalysis`, `Portfolio`, `Alerts`, `Login`, `Register`, `Settings`, `UserCenter`) to `.tsx`
- [x] Convert all components (`ChatbotPanel`, `AuthLayout`, etc.) to `.tsx`
- [x] Verify `npm run build` succeeds without TypeScript or Vite errors
