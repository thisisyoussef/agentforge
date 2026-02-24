# AgentForge

Deploy-first scaffold for the AgentForge project.

## Structure
- `docs/` project planning and assignment docs
- `backend/` FastAPI API for Railway deployment
- `frontend/` placeholder web UI for Railway deployment
- `ghostfolio/` forked product code repository (git submodule)
- `.github/workflows/ci.yml` CI checks
- `DEPLOYMENT_SETUP.md` step-by-step platform setup
- `WORKSPACE.md` master workspace operating model

## Quickstart (local)

### Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/health`.

### Frontend
Open `frontend/index.html` directly in your browser.

## Deployment targets
- Frontend: Railway
- Backend: Railway
- Database: Railway Postgres
- Observability: LangSmith

Follow [DEPLOYMENT_SETUP.md](./DEPLOYMENT_SETUP.md).
