# US-003: Agent NestJS Module + Market Data Tool + Angular Chat UI

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
Deliver the foundational agent stack inside the Ghostfolio fork: new `agent` NestJS module with LangGraph state machine, first tool (`market_data_fetch`), LangSmith tracing, `POST /api/v1/agent/chat` endpoint, and a new Angular chat page. This establishes the pattern every subsequent tool follows and enables manual testing from the browser. Since the agent lives inside Ghostfolio, it deploys as part of the same service.

## Scope
In scope:
1. npm dependencies: `@langchain/langgraph`, `@langchain/anthropic`, `@langchain/core`, `langsmith`, `yahoo-finance2`.
2. New `agent` NestJS module in `ghostfolio/apps/api/src/app/agent/`.
3. `market_data_fetch` tool with typed input/output (Zod schemas or TypeScript interfaces).
4. LangGraph `StateGraph` (reasoning → tool → respond).
5. `POST /api/v1/agent/chat` endpoint via `AgentController`.
6. LangSmith tracing via env vars (`LANGSMITH_API_KEY`, `LANGCHAIN_TRACING_V2`).
7. New Angular chat page at `/agent` route in `ghostfolio/apps/client/`.
8. Five eval test cases (3 happy, 1 edge, 1 error).

Out of scope:
1. Multiple tools (only market_data_fetch).
2. Conversation memory (single-turn only).
3. Error handling middleware (basic try/catch only).
4. Authentication for agent endpoint (open for MVP).

## Pre-Implementation Audit
Local sources to read before writing any code:
1. `ghostfolio/apps/api/src/app/app.module.ts` — root module to register new agent module
2. `ghostfolio/apps/api/src/app/health/health.controller.ts` — pattern for simple controller
3. `ghostfolio/apps/api/src/app/portfolio/portfolio.controller.ts` — pattern for API endpoints
4. `ghostfolio/apps/client/src/app/app-routing.module.ts` — client routing config
5. `ghostfolio/apps/client/src/app/pages/` — pattern for new Angular page
6. `ghostfolio/package.json` — existing dependencies, Nx scripts
7. `docs/IMPLEMENTATION_STRATEGY.md` — Phase 1 exit gate and module structure

## Preparation Phase (Mandatory)
1. Read local code listed in Pre-Implementation Audit.
2. Web-check relevant docs before coding:
   - `@langchain/langgraph` JS quickstart and StateGraph API
   - `@langchain/anthropic` ChatAnthropic tool binding (JS)
   - LangSmith tracing setup (env vars for JS/TS)
   - `yahoo-finance2` npm API (`.quote()`, `.quoteSummary()`)
   - NestJS module/controller/service pattern
   - Angular component + routing setup
3. Write Preparation Notes with:
   - Expected `yahoo-finance2` response shape for a ticker
   - LangGraph state schema design (TypeScript)
   - Agent chat endpoint request/response contract
   - Planned failing tests

### Preparation Notes
_(Fill during execution.)_

Local docs/code reviewed:
1.
2.

Expected yahoo-finance2 data shape:
```typescript
// yahoo-finance2 quote() result keys we need:
// regularMarketPrice, trailingPE, dividendYield, marketCap,
// fiftyTwoWeekHigh, fiftyTwoWeekLow, shortName, symbol
```

Agent chat endpoint contract:
```
POST /api/v1/agent/chat
Request:  {"message": "...", "session_id": "..."}
Response: {"response": "...", "tool_calls": [...], "session_id": "..."}
```

LangGraph state design:
```typescript
interface AgentState {
  messages: BaseMessage[];
  toolCalls?: ToolCall[];
}
```

Error-handling decisions:
1.
2.

Planned failing tests:
1. `market-data.tool.spec.ts: should return price > 0 for valid symbol (AAPL)`
2. `market-data.tool.spec.ts: should return error info for invalid symbol`
3. `agent.controller.spec.ts: should return response with tool call for market question`
4. `agent.controller.spec.ts: should return 200 with error message for empty input`
5. `market-data.tool.spec.ts: should return data for multiple symbols`

## UX Script
Happy path:
1. User navigates to `/agent` page in Ghostfolio and sees chat interface.
2. User types "What is the current price of AAPL?" and clicks send.
3. Loading indicator appears.
4. Response shows AAPL price and tool call details (collapsible).
5. User can ask another question.

Error path:
1. User asks about invalid ticker "XYZNOTREAL".
2. Chat shows graceful error: "Could not find data for XYZNOTREAL."
3. User can ask another question without page refresh.

## Preconditions
- [ ] US-001 complete (Ghostfolio fork + Railway deployment exists)
- [ ] `ANTHROPIC_API_KEY` available (for Claude Sonnet)
- [ ] `LANGSMITH_API_KEY` available (for tracing)

## TDD Plan
Write tests first. Red → Green → Refactor.

### Test files to create/modify
1. `ghostfolio/apps/api/src/app/agent/tools/market-data.tool.spec.ts`
   - `should return price > 0 for valid symbol (AAPL)`
   - `should return error info for invalid symbol (XYZNOTREAL)`
   - `should return data for multiple symbols (MSFT, GOOGL)`
2. `ghostfolio/apps/api/src/app/agent/agent.controller.spec.ts`
   - `should return response with tool call for market question`
   - `should return 200 with error message for empty input`

### Red → Green → Refactor sequence
1. Create test files with all 5 tests. Run `npx nx test api --testPathPattern=agent` — all fail (red).
2. Implement `market-data.tool.ts` → tool tests go green.
3. Implement `agent.service.ts` (LangGraph state machine) and `agent.controller.ts` → controller tests go green.
4. Refactor: extract shared schemas, clean up imports.

## Step-by-step Implementation Plan

### Agent NestJS Module
1. Install npm deps in `ghostfolio/`: `@langchain/langgraph`, `@langchain/anthropic`, `@langchain/core`, `langsmith`, `yahoo-finance2`.
2. Create `ghostfolio/apps/api/src/app/agent/agent.module.ts` — NestJS module.
3. Create `ghostfolio/apps/api/src/app/agent/tools/market-data.tool.ts`:
   - `MarketDataInput` interface: `symbols: string[]`, `metrics?: string[]`.
   - `MarketDataOutput` interface: per-symbol dict with `price`, `peRatio`, `dividendYield`, `marketCap`, `fiftyTwoWeekRange`.
   - `marketDataFetch` function using `yahoo-finance2`.
   - Handle invalid symbols gracefully.
4. Create `ghostfolio/apps/api/src/app/agent/agent.service.ts`:
   - `AgentState` interface with `messages: BaseMessage[]`.
   - Reasoning node (ChatAnthropic with tool binding).
   - Tool execution node.
   - LangGraph `StateGraph` with conditional routing.
5. Create `ghostfolio/apps/api/src/app/agent/agent.controller.ts`:
   - `POST /api/v1/agent/chat` accepting `{ message: string, session_id: string }`.
   - Returns `{ response: string, tool_calls: any[], session_id: string }`.
6. Register `AgentModule` in `app.module.ts`.
7. Configure LangSmith env vars on Railway.

### Angular Chat Page
8. Create `ghostfolio/apps/client/src/app/pages/agent/` directory:
   - `agent-page.component.ts` — page component.
   - `agent-page.component.html` — chat template (dark theme, input + send, message list).
   - `agent-page.component.scss` — styling.
9. Create `ghostfolio/apps/client/src/app/components/chat/` directory:
   - `chat.component.ts` — reusable chat widget.
   - `chat.component.html` — message bubbles, tool call details, loading.
   - `chat.component.scss` — chat styling.
10. Add `/agent` route to client routing module.

### Deploy
11. Commit, push, Railway auto-deploys Ghostfolio (single service).
12. Verify chat UI at `https://<ghostfolio-domain>/agent` and LangSmith traces.

## Implementation Details
_(Fill during execution.)_

Implemented files:
1.
2.

Key interfaces:
```typescript
// Fill during implementation
```

## Acceptance Criteria
- [ ] AC1: Chat UI accessible at Ghostfolio `/agent` page — can send messages and see responses.
- [ ] AC2: `POST /api/v1/agent/chat` with market data question returns structured response with real price data.
- [ ] AC3: Tool calls visible in response payload and in chat UI.
- [ ] AC4: LangSmith project shows at least one traced run with tool call nodes.
- [ ] AC5: All 5 eval test cases pass.
- [ ] AC6: Invalid symbol query returns graceful error in chat, not 500.

## Local Validation
```bash
# Install new dependencies
cd ghostfolio && npm install

# Lint
npx nx lint api

# Tests (story-specific)
npx nx test api --testPathPattern=agent

# Full API test suite
npx nx test api

# Build check
npx nx build api
npx nx build client
```

## Deployment Handoff (Mandatory)
1. Commit all changes in `ghostfolio/`.
2. Push to `main`.
3. Railway auto-deploys Ghostfolio service (single deployment covers API + client).
4. Verify health endpoint still works.
5. Record URL and commit SHA in Checkpoint Result.

## How To Verify In Prod (Required)
- Production URL(s):
  - Ghostfolio (includes agent): `https://ghostfolio-production-c1c7.up.railway.app`
  - Agent chat page: `https://ghostfolio-production-c1c7.up.railway.app/agent`
- Endpoint(s) to call:
  - `POST /api/v1/agent/chat` with `{"message": "What is the price of AAPL?", "session_id": "test-1"}`
- Expected results:
  - Chat page renders at `/agent` with input field and send button
  - Agent returns response with AAPL price (a real number)
  - Response includes `tool_calls` with `market_data_fetch`
  - LangSmith shows traced run
- Failure signals:
  - `/agent` page blank or 404
  - 500 from API
  - No traces in LangSmith
- Rollback action:
  - Revert to previous Ghostfolio deployment on Railway

## User Checkpoint Test
1. Open Ghostfolio → navigate to `/agent` → chat UI renders.
2. Type "What is the current price of AAPL?" → response shows real price.
3. Click tool call details → see structured market data.
4. Type "XYZNOTREAL price" → graceful error, no crash.
5. Check LangSmith → trace visible.

## Checkpoint Result
_(Fill after deployment.)_
- Commit SHA:
- Ghostfolio URL:
- User Validation: `passed | failed | blocked`
- Notes:

## Observability & Monitoring
- Logs to check:
  - Railway Ghostfolio logs (agent execution, tool calls)
- Traces/metrics to check:
  - LangSmith: trace count, latency, tool success rate, token usage
- Alert thresholds:
  - Agent endpoint response >10s
  - Tool failure rate >20%

## Risks & Edge Cases
- Risk 1: `yahoo-finance2` rate limiting or blocking from Railway IPs
- Risk 2: Claude Sonnet API latency causing timeout
- Risk 3: NestJS module registration conflicts with existing Ghostfolio modules
- Risk 4: Angular routing conflicts with existing Ghostfolio pages
- Edge case 1: Yahoo Finance stale/missing data for some symbols
- Edge case 2: User asks non-finance question (agent should still respond)
- Edge case 3: Very long message exceeding context limits

## Notes
- Does NOT depend on US-002 — `market_data_fetch` uses Yahoo Finance, not Ghostfolio.
- Chat UI enables manual testing of all subsequent tools (US-004, US-005).
- LangGraph state machine establishes the pattern all subsequent tools follow.
- Agent module is registered but isolated — does NOT modify existing Ghostfolio modules.
- Uses `@langchain/anthropic` for Claude integration (provides automatic LangSmith tracing).
- Single Railway deployment: agent deploys with Ghostfolio, no separate service needed.
