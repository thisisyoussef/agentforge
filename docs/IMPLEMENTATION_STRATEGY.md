# Overall Implementation Strategy

## Purpose
This document defines the end-to-end execution plan for building the Ghostfolio-based finance agent with a deploy-first approach, story-by-story delivery, and production validation at every step.

## Recommended Repo Model
- Planning, stories, eval docs, and runbooks live in `agentforge`.
- Product code implementation lives in `agentforge/ghostfolio` (fork of `ghostfolio/ghostfolio`).
- Every change maps to a story in `docs/user-stories/`.

## Core Principles
- Infrastructure first, feature second.
- One thin vertical slice before tool expansion.
- Observability early, not late.
- Verification systems are required, not optional.
- Production checks after each meaningful change.

## Phase 0: Infrastructure First (US-001) - Hours 0-3
### Goal
Get Ghostfolio and supporting services running in production before agent feature development.

### Tasks
- Fork Ghostfolio and configure `origin` + `upstream` remotes.
- Deploy Ghostfolio stack on Railway (frontend, backend, Postgres, Redis if required by Ghostfolio runtime).
- Confirm baseline app health and API accessibility.
- Create first Ghostfolio user and generate `GHOSTFOLIO_API_KEY`.
- Document live environment details in `docs/CONTEXT.md`.

### Deliverables
- Reachable Ghostfolio production URL.
- Working API authentication key.
- Updated context snapshot with URLs and commands.

### Exit Gate
- Can log in to Ghostfolio in production.
- Can call one authenticated API endpoint successfully.

### Why this first
Every agent tool depends on a real, stable Ghostfolio target.

## Phase 1: Thin Vertical Slice - Hours 3-12
### Goal
Ship one tool end-to-end through the complete stack:
Agent -> LangGraph node -> Tool -> Ghostfolio API -> Response -> Trace -> Eval.

### Recommended first tool
- `portfolio_analysis` (preferred) or `market_data_fetch`.

### Tasks
- Implement a minimal LangGraph flow with one tool node.
- Define strict tool input/output schema.
- Add LangSmith tracing immediately.
- Add 5 eval test cases for this tool:
  - 3 happy-path
  - 1 edge case
  - 1 error-path

### Deliverables
- One working agent endpoint with trace visibility.
- First eval set and pass/fail report.

### Exit Gate
- Natural language question returns a correct, traced response using real Ghostfolio data.

## Phase 2: Expand to MVP - Hours 12-24
### Goal
Reach MVP behavior with minimum tool coverage and stable conversation behavior.

### Tasks
- Add 2 additional tools (minimum 3 total for MVP).
- Add conversation memory/history.
- Add basic error handling and fallback responses.
- Deploy agent endpoint and run prod smoke checks.

### Deliverables
- 3 working tools.
- Stable multi-turn conversation.
- Basic failure handling.

### Exit Gate
- User asks a natural language question and receives a coherent answer with real tool execution and no crash.

## Phase 3: Eval + Verification Framework - Days 2-4
### Goal
Move from MVP to production-grade reliability signals.

### Tasks
- Expand from 3 to 5 tools (minimum required).
- Build 50-case eval dataset:
  - 20 happy path
  - 10 edge cases
  - 10 adversarial
  - 10 multi-step
- Implement at least 3 verification systems:
  - Fact-checking / source validation
  - Confidence scoring
  - Output validation and guardrails
- Add latency + token metrics dashboard in LangSmith.

### Deliverables
- Repeatable evaluation pipeline.
- Verification layer attached to final response generation.
- Baseline reliability metrics.

### Exit Gate
- Eval dataset runs end-to-end with measurable pass rate and clear failure taxonomy.

## Phase 4: Polish + Open Source - Days 5-7
### Goal
Package and present work for submission/interviews with measurable outcomes.

### Tasks
- Improve toward targets:
  - >80% eval pass
  - >95% tool success
- Package ESG screening capability as open source contribution.
- Create architecture document.
- Create AI cost analysis.
- Record demo video.

### Deliverables
- Public contribution artifact (PR/package/module).
- Final docs and demo package.

### Exit Gate
- Submission-ready repo and demo with reproducible evidence.

## Implementation Additions (Opinionated)
### 1) Start read-only, then add risky logic
Prioritize read-only tools first (portfolio/risk/data lookup) before any recommendation-heavy or compliance-heavy output generation.

### 2) Lock contracts early
Define tool schemas and error contracts early to reduce integration churn as you scale from 1 to 5 tools.

### 3) Classify failures from day 1
Tag failures as data, tool, model, or policy/verification. This accelerates iteration in Phase 3.

### 4) Keep one source of truth for progress
Track phase gates and checklist progress in story files under `docs/user-stories/`.

## Dependency and Secret Setup Notes
### Market data
- Yahoo Finance via `yfinance` requires no API key (free, no signup).
- Alpha Vantage is backup and requires `ALPHA_VANTAGE_API_KEY`.

### Ghostfolio API key flow (chicken-and-egg)
- Deploy Ghostfolio first.
- Create a user account in deployed app.
- Generate API key in-app.
- Save as `GHOSTFOLIO_API_KEY` in Railway backend env.

### Self-generated secrets
Generate strong random values for secrets such as:
- `ACCESS_TOKEN_SALT`
- `JWT_SECRET_KEY`
- `REDIS_PASSWORD`
- `POSTGRES_PASSWORD`

Example:
```bash
openssl rand -hex 32
```

## Story Mapping (Suggested)
- `US-001`: Deploy + fork + runtime baseline.
- `US-002`: Thin vertical slice (single tool + tracing + 5 evals).
- `US-003`: Expand to 3 tools + memory + error handling.
- `US-004`: Expand to 5 tools + verification systems.
- `US-005`: 50-case eval pipeline and dashboard metrics.
- `US-006`: Open-source packaging + final docs/demo.

## Definition of Done (Per Story)
Use `docs/DEFINITION_OF_DONE.md` for required completion checks.

## Daily Execution Rhythm (Recommended)
- Morning: implement one story slice.
- Midday: run tests + deploy.
- Afternoon: run prod verification and evals.
- End of day: update story status, evidence, and next blockers.

## Production Verification Template
Always report:
- Story ID
- Commit SHA
- Deployed URL(s)
- Commands run
- Expected output
- Actual output
- Pass/fail
- Rollback plan
