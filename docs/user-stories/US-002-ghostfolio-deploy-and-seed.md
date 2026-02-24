# US-002: Deploy Ghostfolio on Railway with Seeded Portfolio

## Status
- State: `done`
- Owner: `youssef`
- Depends on: US-001
- Related PR/Commit:
- Target environment: `prod`

## Persona
**Alex, the Agent Developer** wants a live Ghostfolio API target so agent tools can fetch real portfolio data instead of mocks.

## User Story
> As Alex, I want Ghostfolio running in production with a seeded test portfolio so that agent tools have a real API target to call.

## Goal
Deploy the Ghostfolio stack (app + Postgres + Redis) on Railway, create a user account, generate an API key, and seed a diversified test portfolio. Wire the API key into the agentforge backend so tools can authenticate.

## Scope
In scope:
1. Deploy Ghostfolio Docker image (`ghostfolio/ghostfolio:latest`) as a Railway service.
2. Add Railway Postgres and Redis services for Ghostfolio.
3. Configure required secrets (`ACCESS_TOKEN_SALT`, `JWT_SECRET_KEY`, `DATABASE_URL`, `REDIS_*`).
4. Create a user account and generate API key through the Ghostfolio UI.
5. Seed test portfolio with 5-8 holdings across asset classes (AAPL, MSFT, GOOGL, BND, VWO, BTC, XOM).
6. Wire `GHOSTFOLIO_URL` and `GHOSTFOLIO_API_KEY` into agentforge backend env.
7. Update `docs/CONTEXT.md` with Ghostfolio production URL.

Out of scope:
1. Custom Ghostfolio code changes.
2. Schema migrations beyond baseline.
3. SSL or custom domain configuration.

## Pre-Implementation Audit
Local sources to read before any work:
1. `ghostfolio/docker/docker-compose.yml` — Docker image name, service dependencies, env vars
2. `ghostfolio/docker/docker-compose.dev.yml` — Dev env var defaults (Postgres, Redis config)
3. `ghostfolio/.env.dev` — Required env var names and example values
4. `ghostfolio/apps/api/src/app/portfolio/portfolio.controller.ts` — API endpoints for portfolio data
5. `backend/.env.example` — Where to wire Ghostfolio URL and API key

## Preparation Phase (Mandatory)
1. Read local Docker and env config files listed above.
2. Web-check relevant docs:
   - Ghostfolio self-hosting guide (README)
   - Railway Docker deployment docs
   - Railway service networking (internal URLs between services)
3. Write Preparation Notes with:
   - Required env var list with generation method for each
   - API key generation flow (chicken-and-egg: deploy first, create user, then generate key)
   - Seed portfolio composition (tickers, quantities, dates, asset classes)

### Preparation Notes

Local docs/code reviewed:
1. `ghostfolio/docker/docker-compose.yml` — Image `ghostfolio/ghostfolio:latest`, port 3333, depends on postgres (healthy) + redis (healthy), healthcheck at `/api/v1/health`
2. `ghostfolio/docker/docker-compose.dev.yml` — Dev overlay exposing Postgres 5432 and Redis 6379 ports
3. `ghostfolio/.env.dev` — Required env vars: `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `ACCESS_TOKEN_SALT`, `DATABASE_URL`, `JWT_SECRET_KEY`
4. `ghostfolio/.env.example` — Production template; DATABASE_URL uses `postgresql://user:pass@postgres:5432/ghostfolio-db?connect_timeout=300&sslmode=prefer`
5. `ghostfolio/apps/api/src/app/portfolio/portfolio.controller.ts` — Key endpoints: `GET /portfolio/details`, `GET /portfolio/holdings`, `GET /portfolio/performance` (v2). Auth via JWT bearer token.
6. `backend/.env.example` — Has `GHOSTFOLIO_BASE_URL` and `GHOSTFOLIO_API_KEY` placeholders ready
7. `DEPLOYMENT_SETUP.md` — Railway project `agentforge` (id: `a6794fe3-0aa3-4911-bf6b-8ccd995a60f7`) with existing Postgres, backend, frontend services

Existing Railway services (all SUCCESS):
- Postgres (id: `edefcf8a-e8a7-4e7a-b872-242dbaa3a17c`)
- backend (id: `b2f88a04-71aa-4405-b08a-e60406b44d52`)
- frontend (id: `796ea085-6ce2-44bd-bbe0-9855f0a83a9c`)

Required env vars for Ghostfolio service:
1. `DATABASE_URL` — `postgresql://user:pass@<railway-postgres-host>:5432/ghostfolio-db?connect_timeout=300&sslmode=prefer` (new Postgres instance or shared)
2. `REDIS_HOST` — Railway Redis internal hostname
3. `REDIS_PORT` — `6379`
4. `REDIS_PASSWORD` — generated: `945b4b2e69d28eb63a6f1a7e8ec39271`
5. `ACCESS_TOKEN_SALT` — generated: `88140a15a7f33cc1aadf2b2738e1003d323157c0308d752000481790a9b46215`
6. `JWT_SECRET_KEY` — generated: `37d40621fa722196e7e605ab8d32385ef25badec5d4d02b135e5a84d9dd2cb6e`
7. `POSTGRES_DB` — `ghostfolio-db`
8. `POSTGRES_USER` — `user`
9. `POSTGRES_PASSWORD` — (from Railway Postgres provisioning)

API key generation flow (chicken-and-egg):
1. Deploy Ghostfolio with backing services first
2. Wait for health check to pass
3. Open Ghostfolio web UI, create user account (first user gets admin)
4. Navigate to Settings > API Keys > Generate
5. Copy bearer token for use in agentforge backend

Seed portfolio plan:
| Ticker | Asset Class | Quantity | Buy Date   | Purpose |
|--------|------------|----------|------------|---------|
| AAPL   | Equity     | 10       | 2024-01-15 | Clean holding |
| MSFT   | Equity     | 8        | 2024-01-15 | Clean holding |
| GOOGL  | Equity     | 5        | 2024-02-01 | Clean holding |
| BND    | Bond ETF   | 50       | 2024-01-15 | Diversification |
| VWO    | Int'l ETF  | 30       | 2024-03-01 | Diversification |
| BTC    | Crypto     | 0.1      | 2024-01-15 | Crypto exposure |
| XOM    | Equity     | 15       | 2024-02-01 | ESG-flagged (fossil fuels) |

## UX Script
Happy path:
1. Developer deploys Ghostfolio on Railway.
2. Ghostfolio health endpoint returns 200.
3. Developer creates user account through web UI.
4. Developer generates API key in settings.
5. Developer seeds portfolio with buy activities.
6. API call to `/portfolio/details` with bearer token returns holdings.

Error path:
1. Ghostfolio fails to start (missing env var or DB connection).
2. Railway logs show specific error message.
3. Developer fixes env var and redeploys.

## Preconditions
- [ ] US-001 complete (Railway project exists with backend + frontend services)
- [ ] Railway account with capacity for additional services

## TDD Plan
This is an infrastructure story — no application code to TDD. Validation is via deployment checks and API calls.

### Validation sequence
1. Deploy Ghostfolio → verify health endpoint.
2. Create user → verify login works.
3. Generate API key → verify authenticated API call.
4. Seed portfolio → verify holdings count ≥5.
5. Wire env vars → verify backend can read them.

## Step-by-step Implementation Plan
1. Add Ghostfolio Railway service using official Docker image.
2. Add Railway Postgres service and bind `DATABASE_URL`.
3. Add Railway Redis service and bind `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`.
4. Generate secrets: `openssl rand -hex 32` for `ACCESS_TOKEN_SALT` and `JWT_SECRET_KEY`.
5. Set all required env vars on Ghostfolio service.
6. Deploy and wait for health check pass.
7. Open Ghostfolio web UI, create user account.
8. Navigate to settings, generate API key.
9. Seed portfolio: add buy activities for AAPL, MSFT, GOOGL, BND, VWO, BTC, XOM.
10. Verify `GET /api/v1/portfolio/details` returns ≥5 holdings.
11. Add `GHOSTFOLIO_URL` and `GHOSTFOLIO_API_KEY` to agentforge backend env.
12. Update `docs/CONTEXT.md` with new Ghostfolio URL.

## Implementation Details

Implemented/configured:
1. Added Redis service to Railway project (id: `12a7603b-0fba-4245-ba5a-5193eb523f39`, internal: `redis.railway.internal:6379`)
2. Added Postgres-0LHG service for Ghostfolio (id: `2a239a8f-6879-4313-a01d-fa9543bcf567`, internal: `postgres-0lhg.railway.internal:5432`)
3. Deployed `ghostfolio/ghostfolio:latest` Docker image as Railway service with env vars: `DATABASE_URL`, `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`, `ACCESS_TOKEN_SALT`, `JWT_SECRET_KEY`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
4. Generated public domain: `https://ghostfolio-production-c1c7.up.railway.app` (port 3333)
5. Health endpoint verified: `GET /api/v1/health` returns HTTP 200
6. Created admin user account (User ID: `5ed0a3c5-57fa-4ae1-8c38-417d9ee1e58b`)
7. Security token generated and stored for API auth
8. Created brokerage account "Test Brokerage" (id: `eb5d297a-398c-482d-ae0c-7ad20270597b`)
9. Created 7 asset profiles via admin API (MANUAL data source — Yahoo Finance not available on Railway)
10. Imported 7 buy activities via `/api/v1/import` endpoint
11. Updated `GHOSTFOLIO_BASE_URL` and `GHOSTFOLIO_API_KEY` on backend Railway service
12. Updated `docs/CONTEXT.md` with Ghostfolio production URL and auth details

Note: Yahoo Finance data source is listed but non-functional on Railway (symbol lookup returns only CoinGecko results). Used MANUAL data source as workaround. Holdings use UUID symbols internally but display ticker names in the UI. Extra Redis-8FmJ service was accidentally created and should be cleaned up manually from Railway dashboard.

## Acceptance Criteria
- [x] AC1: Ghostfolio health endpoint (`GET /api/v1/health`) returns 200.
- [x] AC2: User account exists with a valid API key (security token for auth).
- [x] AC3: Portfolio details endpoint returns ≥5 holdings with bearer token (7 holdings confirmed).
- [x] AC4: Agentforge backend env has `GHOSTFOLIO_BASE_URL` and `GHOSTFOLIO_API_KEY` set.
- [x] AC5: All three Railway services (Ghostfolio, Postgres-0LHG, Redis) show SUCCESS.
- [x] AC6: XOM included in seed portfolio (needed for US-005 ESG compliance demo).

## Local Validation
```bash
# No local code changes — validate via Railway dashboard and API calls
# Verify Ghostfolio health (replace URL after deploy)
# Open in browser: https://<ghostfolio-domain>/api/v1/health
# Open in browser: https://<ghostfolio-domain> (web UI login)
```

## Deployment Handoff (Mandatory)
1. Deploy Ghostfolio + Postgres + Redis on Railway.
2. Configure all env vars.
3. Create user and seed portfolio through Ghostfolio UI.
4. Wire API key into agentforge backend env.
5. Record URLs and env state in Checkpoint Result.

## How To Verify In Prod (Required)
- Production URL(s):
  - Ghostfolio: `https://ghostfolio-production-c1c7.up.railway.app`
- Browser verification:
  1. Open `https://ghostfolio-production-c1c7.up.railway.app/api/v1/health` → expect `200 OK`
  2. Open `https://ghostfolio-production-c1c7.up.railway.app` → click "Sign in" → enter security token → see dashboard
  3. Navigate to Portfolio > Activities → expect 7 activities listed (AAPL, MSFT, GOOGL, BND, VWO, BTC-USD, XOM)
  4. Confirm XOM appears in the list
- Failure signals:
  - Non-200 health response
  - Empty portfolio data
  - Redis/Postgres connection errors in logs
- Rollback action:
  - Remove Ghostfolio Railway services; agentforge backend/frontend unaffected

## User Checkpoint Test
1. Open Ghostfolio web UI → verify login works.
2. Navigate to portfolio → verify all 7 seeded holdings visible.
3. Check that XOM appears (needed for ESG compliance demo in US-005).
4. Verify API key works by checking backend logs for successful Ghostfolio calls (in later stories).

## Checkpoint Result
- Commit SHA: (pending commit)
- Ghostfolio URL: `https://ghostfolio-production-c1c7.up.railway.app`
- User Validation: `passed`
- Notes:
  - Health endpoint returns 200 ✓
  - 7 holdings visible in Activities UI (AAPL, MSFT, GOOGL, BND, VWO, BTC-USD, XOM) ✓
  - XOM present for ESG compliance demo ✓
  - Portfolio details API returns 7 holdings with bearer token ✓
  - Backend env vars updated with correct Ghostfolio URL and security token ✓
  - Yahoo Finance data source non-functional on Railway (known limitation, using MANUAL data source)
  - Extra Redis-8FmJ service needs manual cleanup from Railway dashboard

## Observability & Monitoring
- Logs to check:
  - Railway Ghostfolio service logs (startup, DB connection)
  - Railway Postgres and Redis logs
- Traces/metrics to check:
  - N/A (no agent traces yet)
- Alert thresholds:
  - Health endpoint failure or sustained 5xx

## Risks & Edge Cases
- Risk 1: Ghostfolio Docker image requires specific config not documented
- Risk 2: Chicken-and-egg — need running app to create user and generate API key
- Risk 3: Railway resource limits (Postgres + Redis + Ghostfolio may need paid plan)
- Edge case 1: Ghostfolio DB migrations fail on fresh Postgres
- Edge case 2: Redis not ready before Ghostfolio starts (startup order)

## Notes
- This story can run in parallel with US-003 since the first agent tool uses Yahoo Finance, not Ghostfolio.
- XOM is intentionally included as an ESG-flagged holding for US-005 compliance checker demo.
- Ghostfolio docker-compose reference: `ghostfolio/docker/docker-compose.yml`
- Env var reference: `ghostfolio/.env.dev`
