# US-003: Thin Vertical Slice — Market Data Tool + LangGraph + Chat UI

## Status
- State: `todo`
- Owner: `youssef`
- Depends on: US-001
- Related PR/Commit:
- Target environment: `prod`

## Persona
**Alex, the Agent Developer** wants to prove the full stack works end-to-end (user question → agent → tool → real data → response) with a testable UI.

**Sam, the End User** wants to ask natural language questions about stock prices and get real answers.

## User Story
> As Sam, I want to ask natural language questions about stock prices through a chat interface so that I get structured financial information without using APIs directly.
> As Alex, I want a working chat UI from day one so that I can manually test every tool as it's built.

## Goal
Deliver the foundational agent stack: LangGraph state machine, first tool (`market_data_fetch`), LangSmith tracing, `/agent/chat` endpoint, and a minimal browser chat UI. This establishes the pattern every subsequent tool follows and enables manual testing from the browser.

## Scope
In scope:
1. Python dependencies: `langchain-anthropic`, `langgraph`, `langsmith`, `yfinance`, `pydantic`.
2. `market_data_fetch` tool with typed input/output schemas.
3. LangGraph state machine (reasoning → tool → respond).
4. `POST /agent/chat` endpoint.
5. LangSmith tracing via env vars.
6. Minimal chat UI (vanilla HTML/CSS/JS, dark theme).
7. Five eval test cases (3 happy, 1 edge, 1 error).

Out of scope:
1. Multiple tools (only market_data_fetch).
2. Conversation memory (single-turn only).
3. Error handling middleware (basic try/catch only).
4. Rich UI framework.

## Pre-Implementation Audit
Local sources to read before writing any code:
1. `backend/app/main.py` — existing FastAPI app structure, CORS config
2. `backend/requirements.txt` — current dependencies
3. `backend/.env.example` — env var names for LLM and LangSmith
4. `frontend/index.html` — current placeholder to replace
5. `docs/IMPLEMENTATION_STRATEGY.md` — Phase 1 exit gate and tool schema guidance

## Preparation Phase (Mandatory)
1. Read local code listed in Pre-Implementation Audit.
2. Web-check relevant docs before coding:
   - LangGraph quickstart and StateGraph API
   - `langchain-anthropic` ChatAnthropic tool binding
   - LangSmith tracing setup (env vars)
   - `yfinance` Ticker API (`.info`, `.fast_info`)
   - Pydantic v2 model definition
3. Write Preparation Notes with:
   - Expected `yfinance` response shape for a ticker
   - LangGraph state schema design
   - Agent chat endpoint request/response contract
   - Planned failing tests

### Preparation Notes
_(Fill during execution.)_

Local docs/code reviewed:
1.
2.

Expected yfinance data shape:
```python
# ticker.info keys we need:
# currentPrice, trailingPE, dividendYield, marketCap,
# fiftyTwoWeekHigh, fiftyTwoWeekLow, shortName
```

Agent chat endpoint contract:
```
POST /agent/chat
Request:  {"message": "...", "session_id": "..."}
Response: {"response": "...", "tool_calls": [...], "session_id": "..."}
```

Error-handling decisions:
1.
2.

Planned failing tests:
1. `test_market_data_fetch_valid_symbol` — AAPL returns price > 0
2. `test_market_data_fetch_invalid_symbol` — XYZNOTREAL returns error info
3. `test_agent_chat_market_question` — chat endpoint returns response with tool call
4. `test_agent_chat_empty_message` — empty message returns 200 with error
5. `test_market_data_multi_symbol` — MSFT+GOOGL returns both

## UX Script
Happy path:
1. User opens frontend URL in browser and sees chat interface.
2. User types "What is the current price of AAPL?" and clicks send.
3. Loading indicator appears.
4. Response shows AAPL price and tool call details (collapsible).
5. User can ask another question.

Error path:
1. User asks about invalid ticker "XYZNOTREAL".
2. Chat shows graceful error: "Could not find data for XYZNOTREAL."
3. User can ask another question without page refresh.

## Preconditions
- [ ] US-001 complete (backend + frontend deployed on Railway)
- [ ] `ANTHROPIC_API_KEY` available (for Claude Sonnet)
- [ ] `LANGSMITH_API_KEY` available (for tracing)

## TDD Plan
Write tests first. Red → Green → Refactor.

### Test files to create/modify
1. `backend/tests/test_market_data.py`
   - `test_fetch_valid_symbol` — `market_data_fetch("AAPL")` returns dict with `price` > 0
   - `test_fetch_invalid_symbol` — `market_data_fetch("XYZNOTREAL")` returns error info, no exception
   - `test_fetch_multiple_symbols` — `market_data_fetch(["MSFT", "GOOGL"])` returns data for both
2. `backend/tests/test_agent_chat.py`
   - `test_chat_market_question` — `POST /agent/chat` with "What is the price of AAPL?" returns 200, response contains price, `tool_calls` non-empty
   - `test_chat_empty_message` — `POST /agent/chat` with `""` returns 200, not 500

### Red → Green → Refactor sequence
1. Create test files with all 5 tests. Run — all fail (red).
2. Implement `backend/app/tools/market_data.py` — `test_fetch_*` tests go green.
3. Implement `backend/app/agent/graph.py` and update `main.py` — `test_chat_*` tests go green.
4. Refactor: extract shared schemas, clean up imports.

## Step-by-step Implementation Plan

### Agent Infrastructure
1. Add deps to `backend/requirements.txt`.
2. Create `backend/app/tools/__init__.py`.
3. Create `backend/app/tools/market_data.py`:
   - `MarketDataInput` schema: `symbols: list[str]`, `metrics: list[str] | None`.
   - `MarketDataOutput` schema: per-symbol dict with `price`, `pe_ratio`, `dividend_yield`, `market_cap`, `52_week_range`.
   - `market_data_fetch` function using `yfinance`.
   - Handle invalid symbols gracefully.
4. Create `backend/app/agent/__init__.py`.
5. Create `backend/app/agent/graph.py`:
   - `AgentState` TypedDict with `messages: list`.
   - Reasoning node (Claude Sonnet with tool binding).
   - Tool execution node.
   - LangGraph `StateGraph` with conditional routing.
6. Add `POST /agent/chat` endpoint to `main.py`.
7. Configure LangSmith env vars.

### Chat UI
8. Replace `frontend/index.html`:
   - Dark theme, text input + send button, scrollable message history.
   - Tool calls as collapsible `<details>`.
   - Loading indicator.
   - `session_id` via `crypto.randomUUID()` in `sessionStorage`.
   - Calls `POST /agent/chat` on backend URL.

### Deploy
9. Deploy backend and frontend to Railway.
10. Verify chat UI and LangSmith traces.

## Implementation Details
_(Fill during execution.)_

Implemented files:
1.
2.

Key interfaces:
```python
# Fill during implementation
```

## Acceptance Criteria
- [ ] AC1: Chat UI accessible at frontend Railway URL — can send messages and see responses.
- [ ] AC2: `POST /agent/chat` with market data question returns structured response with real price data.
- [ ] AC3: Tool calls visible in response payload and in chat UI.
- [ ] AC4: LangSmith project shows at least one traced run with tool call nodes.
- [ ] AC5: All 5 eval test cases pass.
- [ ] AC6: Invalid symbol query returns graceful error in chat, not 500.

## Local Validation
```bash
# Lint (if configured)
cd backend && python -m py_compile app/main.py app/tools/market_data.py app/agent/graph.py

# Tests (story-specific)
cd backend && pytest tests/test_market_data.py tests/test_agent_chat.py -v

# Full test suite
cd backend && pytest -q

# Build check (Dockerfile)
cd backend && docker build -t agentforge-backend .
```

## Deployment Handoff (Mandatory)
1. Commit all backend + frontend changes.
2. Push to `main`.
3. Railway auto-deploys both services.
4. Verify health endpoint still works.
5. Record URLs and commit SHA in Checkpoint Result.

## How To Verify In Prod (Required)
- Production URL(s):
  - Frontend (chat UI): `https://<frontend-domain>`
  - Backend (API): `https://<backend-domain>`
- Endpoint(s) to call:
  - `POST /agent/chat` with `{"message": "What is the price of AAPL?", "session_id": "test-1"}`
- Expected results:
  - Chat UI renders with dark theme, input field, send button
  - Agent returns response with AAPL price (a real number)
  - Response includes `tool_calls` with `market_data_fetch`
  - LangSmith shows traced run
- Failure signals:
  - Chat UI blank or no response
  - 500 from backend
  - No traces in LangSmith
- Rollback action:
  - Revert to previous Railway deployment

## User Checkpoint Test
1. Open frontend URL → chat UI renders with dark theme.
2. Type "What is the current price of AAPL?" → response shows real price.
3. Click tool call details → see structured market data.
4. Type "XYZNOTREAL price" → graceful error, no crash.
5. Check LangSmith → trace visible.

## Checkpoint Result
_(Fill after deployment.)_
- Commit SHA:
- Frontend URL:
- Backend URL:
- User Validation: `passed | failed | blocked`
- Notes:

## Observability & Monitoring
- Logs to check:
  - Railway backend logs (agent execution, tool calls)
- Traces/metrics to check:
  - LangSmith: trace count, latency, tool success rate, token usage
- Alert thresholds:
  - Agent endpoint response >10s
  - Tool failure rate >20%

## Risks & Edge Cases
- Risk 1: `yfinance` rate limiting or blocking from Railway IPs
- Risk 2: Claude Sonnet API latency causing frontend timeout
- Risk 3: LangSmith tracing overhead
- Edge case 1: Yahoo Finance stale/missing data for some symbols
- Edge case 2: User asks non-finance question (agent should still respond)
- Edge case 3: Very long message exceeding context limits

## Notes
- Does NOT depend on US-002 — `market_data_fetch` uses Yahoo Finance, not Ghostfolio.
- Chat UI enables manual testing of all subsequent tools (US-004, US-005).
- LangGraph state machine establishes the pattern all subsequent tools follow.
- Use `langchain-anthropic` for Claude integration (provides automatic LangSmith tracing).
