# Deploy-First Setup (Vercel + Railway + LangSmith)

This repository now includes a deployable baseline before feature implementation:
- `frontend/` -> static site for Vercel
- `backend/` -> FastAPI service for Railway
- `.github/workflows/ci.yml` -> backend test checks on PR/push

## 1) What is already set up in code
- Railway-ready backend start command in `backend/railway.toml`
- Docker fallback in `backend/Dockerfile`
- Health endpoint at `GET /health`
- Environment variable template in `backend/.env.example`
- Vercel-ready static frontend in `frontend/`

## 2) What you need to do (account/platform setup)
1. Create a Railway project for backend.
2. Connect this GitHub repo and set root directory to `backend`.
3. Add a Railway PostgreSQL service in the same project.
4. Add backend env vars from `backend/.env.example`.
5. Create a Vercel project for frontend.
6. Connect this GitHub repo and set root directory to `frontend`.
7. Add `NEXT_PUBLIC_API_BASE_URL` (or `API_BASE_URL`) in Vercel once backend URL is known.
8. Create a LangSmith project and copy API key into Railway env vars.

## 3) Recommended Railway environment variables (minimum)
- `OPENAI_API_KEY`
- `MODEL_NAME` (default `gpt-5`)
- `LANGSMITH_API_KEY`
- `LANGSMITH_PROJECT=agentforge`
- `LANGSMITH_TRACING=true`
- `DATABASE_URL` (Railway will provide this for Postgres)

## 4) Smoke test after deploy
- Backend: open `https://<railway-domain>/health` -> should return `{ "status": "ok" }`
- Frontend: open Vercel URL -> should show "AgentForge Deployment Baseline"
- CI: confirm GitHub Actions `CI` workflow is green on `main`

## 5) Immediate next implementation steps
1. Add real API routes in `backend/app/` for tool execution.
2. Add DB migrations and schema for traces/audit artifacts.
3. Replace frontend placeholder with chat UI.
4. Wire frontend calls to backend using `API_BASE_URL`.
5. Add integration tests for at least one tool path.
