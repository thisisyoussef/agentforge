# US-001 Railway Deploy and Fork Setup

## Story Metadata
- Story ID: `US-001`
- Title: Deploy frontend and backend on Railway and set up upstream fork workflow
- Status: `todo`
- Priority: `P0`
- Owner: `youssef`
- Related PR/Commit:
- Target environment: `prod`

## User Story
As a project owner,
I want both frontend and backend deployed on Railway and the upstream fork workflow configured,
so that I can validate changes in production continuously and contribute to the target open-source repo safely.

## Scope
### In scope
- Deploy `backend/` as Railway service
- Deploy `frontend/` as Railway service
- Attach Railway Postgres to backend
- Configure minimum production env vars
- Verify public URLs and health checks
- Configure fork + upstream remotes for the target domain repo

### Out of scope
- Implementing domain features
- Database schema/migrations beyond baseline setup
- Production hardening beyond baseline observability/env config

## Preconditions
- [ ] Railway account and project access
- [ ] GitHub access to this repository and fork target repository
- [ ] API keys available (`OPENAI_API_KEY`, `LANGSMITH_API_KEY`)

## Step-by-step Implementation Plan
1. Create Railway project and add `backend` service (root dir `backend`).
2. Create Railway project service for `frontend` (root dir `frontend`).
3. Add Railway Postgres service and bind `DATABASE_URL` to backend.
4. Add env vars from `backend/.env.example`.
5. Deploy both services and capture production URLs.
6. Run smoke checks for backend health and frontend page.
7. Fork the target upstream domain repo (e.g. Ghostfolio).
8. Clone fork locally and add `upstream` remote.
9. Document fork URLs/remotes for future story execution.

## Acceptance Criteria
- [ ] AC1: Backend returns `200` and `{"status":"ok"}` from `/health`.
- [ ] AC2: Frontend Railway URL renders deployment baseline page.
- [ ] AC3: Backend and frontend deploy from `main` via Railway connected GitHub repo.
- [ ] AC4: Upstream fork exists and local clone has both `origin` and `upstream` remotes configured.

## Test Plan
### Unit tests
- [ ] Backend CI tests pass (`pytest -q`)

### Integration tests
- [ ] Frontend can reach backend base URL (once wired)

### End-to-end / production checks
- [ ] `curl -i https://<backend-domain>/health`
- [ ] Open `https://<frontend-domain>/` in browser

## Deployment Plan (Required)
1. Deploy backend on Railway.
2. Deploy frontend on Railway.
3. Bind database and environment variables.
4. Validate both services from public internet.

## How To Verify In Prod (Required)
- Production URL(s):
  - Backend: `https://<backend-domain>`
  - Frontend: `https://<frontend-domain>`
- Endpoint(s) to call:
  - `GET /health`
- Exact commands:
```bash
curl -i https://<backend-domain>/health
```
- Expected results:
  - HTTP `200`
  - JSON body: `{"status":"ok"}`
  - Frontend page contains text: `AgentForge Deployment Baseline`
- Failure signals:
  - Non-200 health response
  - Timeout or DNS failure
  - Frontend 5xx or blank page
- Rollback action:
  - Roll back to last healthy Railway deployment for affected service

## Observability & Monitoring
- Logs to check:
  - Railway backend logs
  - Railway frontend logs
- Traces/metrics to check:
  - LangSmith traces for backend requests (after agent routes are added)
- Alert thresholds:
  - Health endpoint failure or sustained 5xx rates

## Risks & Edge Cases
- Risk 1: Missing env vars causing startup failure
- Risk 2: Incorrect Railway root directory per service
- Edge case 1: Railway domain provisioning delay
- Edge case 2: Fork created but upstream remote not configured locally

## Notes
- This story should be completed before feature implementation stories.
