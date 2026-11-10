# 01: Repo Cleanup and Prefactoring

**What to build:** Remove obsolete duplicate mock services in the frontend, dead imports, and leftover scratch debug text dumps in the repository to clean up technical debt and ensure a clean starting point for TypeScript migration and containerization.

**Blocked by:** None (can start immediately)

**Status:** resolved

- [x] Remove unused `dashboard-frontend/src/mock/` folder and `dashboard-frontend/src/api/` folder (which were dead duplicates of `src/services/api.js` and `src/mocks/`)
- [x] Remove unused `dashboard-frontend/src/mockData.js`
- [x] Remove scratch debug outputs in `Decision/` (`debug_2.txt`, `debug_output.txt`, `models.txt`)
- [x] Verify existing Python tests still pass
