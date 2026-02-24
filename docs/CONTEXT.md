# Live Context Snapshot

Last updated: 2026-02-24

## Repo roles
- Coordination workspace: `https://github.com/thisisyoussef/agentforge`
- Product fork (implementation): `https://github.com/thisisyoussef/ghostfolio`
- Upstream source: `https://github.com/ghostfolio/ghostfolio.git`

## Local paths
- Workspace root: `/Users/youss/Development/gauntlet/agentforge`
- Product code path: `/Users/youss/Development/gauntlet/agentforge/ghostfolio`

## Railway (agentforge project)
- Project name: `agentforge`
- Project id: `a6794fe3-0aa3-4911-bf6b-8ccd995a60f7`
- Backend URL: `https://backend-production-61f8.up.railway.app`
- Frontend URL: `https://frontend-production-a5e0.up.railway.app`
- Backend health endpoint: `https://backend-production-61f8.up.railway.app/health`
- Ghostfolio URL: `https://ghostfolio-production-c1c7.up.railway.app`
- Ghostfolio health: `https://ghostfolio-production-c1c7.up.railway.app/api/v1/health`
- Ghostfolio services: app (Docker image) + Postgres-0LHG + Redis

## Ghostfolio auth
- Auth flow: POST security token to `/api/v1/auth/anonymous` → receive JWT bearer token
- User ID: `5ed0a3c5-57fa-4ae1-8c38-417d9ee1e58b` (admin)
- Security token stored in `GHOSTFOLIO_API_KEY` backend env var
- Seeded portfolio: 7 holdings (AAPL, MSFT, GOOGL, BND, VWO, BTC-USD, XOM) via MANUAL data source

## Current workflow
- Plan and track in `docs/user-stories/`.
- Implement feature code in `ghostfolio/` on story-specific branches.
- Deploy and verify in prod for every completed change.

## Standard prod verification
- Backend health: `https://backend-production-61f8.up.railway.app/health`
- Frontend: `https://frontend-production-a5e0.up.railway.app/`
- Ghostfolio health: `https://ghostfolio-production-c1c7.up.railway.app/api/v1/health`
- Ghostfolio UI: `https://ghostfolio-production-c1c7.up.railway.app` (sign in with security token)

## Open decisions (update as needed)
- Confirm next active story ID.
- Yahoo Finance data provider not working on Railway (using MANUAL data source for now); investigate if needed for live price feeds.
