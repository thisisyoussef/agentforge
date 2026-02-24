# Deploy-First Setup (Railway + Railway + LangSmith)

This repository now includes a deployable baseline before feature implementation:
- `frontend/` -> static site for Railway
- `backend/` -> FastAPI service for Railway
- `.github/workflows/ci.yml` -> backend test checks on PR/push

## 1) What is already set up in code
- Railway-ready backend start command in `backend/railway.toml`
- Docker fallback in `backend/Dockerfile`
- Health endpoint at `GET /health`
- Environment variable template in `backend/.env.example`
- Railway-ready static frontend in `frontend/railway.toml` + `frontend/Dockerfile`

## 2) What you need to do (account/platform setup)
1. Create one Railway project.
2. Add a `backend` service from this repo with root directory `backend`.
3. Add a `frontend` service from this repo with root directory `frontend`.
4. Add a Railway PostgreSQL service in the same project.
5. Add backend env vars from `backend/.env.example`.
6. Add frontend env var `API_BASE_URL` (once backend URL is known).
7. Create a LangSmith project and copy API key into Railway backend env vars.

## 3) Recommended Railway environment variables (minimum)
- `OPENAI_API_KEY`
- `MODEL_NAME` (default `gpt-5`)
- `LANGSMITH_API_KEY`
- `LANGSMITH_PROJECT=agentforge`
- `LANGSMITH_TRACING=true`
- `DATABASE_URL` (Railway will provide this for Postgres)

## 4) Smoke test after deploy
- Backend: open `https://<railway-domain>/health` -> should return `{ "status": "ok" }`
- Frontend: open Railway frontend URL -> should show "AgentForge Deployment Baseline"
- CI: confirm GitHub Actions `CI` workflow is green on `main`

## 5) Immediate next implementation steps
1. Add real API routes in `backend/app/` for tool execution.
2. Add DB migrations and schema for traces/audit artifacts.
3. Replace frontend placeholder with chat UI.
4. Wire frontend calls to backend using `API_BASE_URL`.
5. Add integration tests for at least one tool path.

## 6) Fork strategy (recommended for this project)
You should fork the original domain repo and build your agent contribution there.

Upstream source repository:
- `https://github.com/ghostfolio/ghostfolio.git`

Recommended approach:
1. Keep this `agentforge` repo as your planning/agent-app workspace.
2. Fork `ghostfolio/ghostfolio` to your GitHub account.
3. Clone your fork and add upstream remote:
   - `git clone https://github.com/<your-username>/ghostfolio.git`
   - `cd ghostfolio`
   - `git remote add upstream https://github.com/ghostfolio/ghostfolio.git`
   - `git remote -v`
4. Sync with upstream regularly:
   - `git fetch upstream`
   - `git checkout main`
   - `git merge upstream/main`
   - `git push origin main`
5. Implement the domain-specific agent features in your fork.
6. Link both repos in your final submission:
   - this repo: planning, architecture, eval docs, deployment notes
   - forked repo: concrete open-source contribution and PR history
