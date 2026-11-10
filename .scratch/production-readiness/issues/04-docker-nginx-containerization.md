# 04: Docker and Nginx Containerization

**What to build:** Multi-stage production container build for `dashboard-frontend` served by Alpine Nginx with reverse proxy to FastAPI, integrated into `docker-compose.yml` alongside the backend and Streamlit dashboard.

**Blocked by:** 02: FastAPI Production Routers, 03: Frontend TypeScript Migration

**Status:** resolved

- [x] Create `dashboard-frontend/Dockerfile` with multi-stage build (Node 22 builder -> Alpine Nginx)
- [x] Create `dashboard-frontend/nginx.conf` supporting SPA fallback routing and proxying `/api/` to backend
- [x] Update `docker-compose.yml` to define the `frontend` service mapping port 3000 to Nginx container
- [x] Add `.dockerignore` for `dashboard-frontend` (ignoring `node_modules`, `dist`, etc.)
- [x] Verify `docker-compose config` syntax and port assignments
