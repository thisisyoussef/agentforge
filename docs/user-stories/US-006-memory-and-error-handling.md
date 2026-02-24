# US-006: Conversation Memory and Error Handling

## Status
- State: `todo`
- Owner: `youssef`
- Depends on: US-003, US-004, US-005
- Related PR/Commit:
- Target environment: `prod`

## Persona
**Sam, the End User** wants to have a natural multi-turn conversation without repeating context each time.

**Jordan, the Observer** wants obvious error states so AI usage feels trustworthy and predictable.

## User Story
> As Sam, I want multi-turn conversation so that I can ask follow-up questions without restating context.
> As Jordan, I want clear error messages when something fails so I always know what's happening.

## Goal
Add session-based conversation memory (messages persist across turns per session) and classified error handling (tool/data/model/service errors produce user-friendly messages, not stack traces). This completes MVP requirements #5 (conversation history) and #6 (error handling).

## Scope
In scope:
1. Session-based memory in LangGraph state (in-memory `Map<string, BaseMessage[]>` keyed by `session_id`).
2. Error handling with classified error types in NestJS.
3. Tool failure → fallback message.
4. LLM API failure → retry/timeout message.
5. Portfolio service unavailable → "portfolio service unavailable" message.
6. Error classification: `DataError`, `ToolError`, `ModelError`, `ServiceError`.
7. Angular chat component error display styling.
8. Four eval test cases (2 multi-turn + 2 error).

Out of scope:
1. Persistent session storage (in-memory only, lost on restart).
2. Authentication or user identity.
3. Session expiry or cleanup logic.
4. Chat UI creation (already exists from US-003).

## Pre-Implementation Audit
Local sources to read before writing any code:
1. `ghostfolio/apps/api/src/app/agent/agent.service.ts` — current AgentState and graph to extend with memory
2. `ghostfolio/apps/api/src/app/agent/agent.controller.ts` — current endpoint to add error handling
3. `ghostfolio/apps/api/src/app/agent/tools/market-data.tool.ts` — understand current error patterns
4. `ghostfolio/apps/api/src/app/agent/tools/portfolio-analysis.tool.ts` — Ghostfolio error patterns
5. `ghostfolio/apps/client/src/app/components/chat/chat.component.ts` — chat UI to add error styling

## Preparation Phase (Mandatory)
1. Read local code listed above.
2. Web-check relevant docs:
   - LangGraph JS message history / checkpointer patterns
   - LangGraph state persistence approaches (JS/TS)
   - NestJS exception filters and error handling
3. Write Preparation Notes.

### Preparation Notes
_(Fill during execution.)_

Local docs/code reviewed:
1.
2.

Memory design:
```typescript
// In-memory session store (inside AgentService)
private sessions = new Map<string, BaseMessage[]>();

// On each /api/v1/agent/chat call:
// 1. Look up session_id in sessions map
// 2. Prepend history to current messages
// 3. Invoke graph
// 4. Append new messages to session history
```

Error classification:
```typescript
enum ErrorType {
  DATA = 'data',       // yahoo-finance2/external data issues
  TOOL = 'tool',       // tool execution failure
  MODEL = 'model',     // LLM API failure
  SERVICE = 'service', // Ghostfolio/dependency down
}

interface AgentError {
  type: ErrorType;
  message: string;     // user-friendly
  recoverable: boolean;
}
```

Planned failing tests:
1. `should carry context from first message to second message`
2. `should handle tool switching within same session (portfolio → compliance)`
3. `should return 200 with user-friendly error for empty input`
4. `should return graceful error when simulating service failure`

## UX Script
Happy path (multi-turn):
1. User asks "What's the price of AAPL?"
2. Agent responds with price.
3. User asks "How about Microsoft?" (no ticker specified).
4. Agent understands from context → responds with MSFT price.

Error path:
1. Portfolio service unavailable.
2. User asks "What's my portfolio risk?"
3. Agent responds: "I'm unable to access portfolio data right now. I can still help with market data — try asking about stock prices."
4. User asks "Price of AAPL?" → works fine (different tool).

## Preconditions
- [ ] US-003 complete (LangGraph agent + Angular chat page + market_data tool)
- [ ] US-004 complete (portfolio_risk_analysis tool)
- [ ] US-005 complete (compliance_check tool)

## TDD Plan
Write tests first. Red → Green → Refactor.

### Test files to create/modify
1. `ghostfolio/apps/api/src/app/agent/memory/session-memory.service.spec.ts`
   - `should carry context from first message to second`
   - `should handle tool switching within same session`
   - `should keep independent sessions separate`
2. `ghostfolio/apps/api/src/app/agent/errors/agent-error.spec.ts`
   - `should return 200 with user-friendly error for empty input`
   - `should return 200 with graceful error for long input`
   - `should classify errors with correct ErrorType`

### Red → Green → Refactor sequence
1. Write all tests. Run `npx nx test api --testPathPattern=agent` — all fail (red).
2. Implement session memory service → memory tests go green.
3. Implement error handling (NestJS exception filter + error classes) → error tests go green.
4. Refactor: clean up error classification, add to all tools.

## Step-by-step Implementation Plan

### Memory
1. Create `ghostfolio/apps/api/src/app/agent/memory/session-memory.service.ts`:
   - `SessionMemoryService` — NestJS injectable.
   - In-memory `Map<string, BaseMessage[]>`.
   - `getHistory(sessionId)` and `addMessages(sessionId, messages)` methods.
   - LRU eviction (max 1000 sessions) to prevent unbounded growth.
2. Update `agent.service.ts` to inject `SessionMemoryService`.
3. Prepend session history before graph invocation, append after.

### Error Handling
4. Create `ghostfolio/apps/api/src/app/agent/errors/agent-error.ts`:
   - `ErrorType` enum and `AgentError` class.
5. Wrap tool execution in `agent.service.ts` with classified try/catch.
6. Add NestJS exception filter in agent module — catch unhandled → return 200 with error.
7. Log errors with classification for debugging and LangSmith traces.

### Chat UI
8. Update Angular chat component — error responses styled with amber/red border.

### Deploy
9. Deploy (single Ghostfolio service) and test multi-turn + error scenarios.

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
- [ ] AC1: Second message references context from first (verified by test).
- [ ] AC2: Service outage → user-friendly error, not 500/stack trace.
- [ ] AC3: Invalid input (empty, very long) → graceful response.
- [ ] AC4: Error classification visible in logs/LangSmith traces.
- [ ] AC5: All TDD test cases pass.

## Local Validation
```bash
# Tests (story-specific)
cd ghostfolio && npx nx test api --testPathPattern="memory|error"

# Full API test suite
npx nx test api

# Build
npx nx build api
npx nx build client
```

## Deployment Handoff (Mandatory)
1. Commit changes in `ghostfolio/`.
2. Push to `main` → Railway auto-deploys Ghostfolio.
3. Verify health endpoint.
4. Test multi-turn and error scenarios via chat UI at `/agent`.
5. Record in Checkpoint Result.

## How To Verify In Prod (Required)
- Production URL(s):
  - Ghostfolio: `https://ghostfolio-production-e8d1.up.railway.app`
  - Chat page: `https://ghostfolio-production-e8d1.up.railway.app/agent`
- Expected results:
  - "Price of AAPL?" then "How about Microsoft?" → MSFT data (context maintained)
  - Empty message → user-friendly error, no crash
  - Logs show error classification for failures
- Failure signals:
  - Agent treats each message as independent (no memory)
  - 500 on invalid input
  - Stack traces visible in chat
- Rollback action:
  - Revert Ghostfolio deployment; all tools still work (just without memory/error handling)

## User Checkpoint Test
1. Ask "What is AAPL's price?" → get response.
2. Ask "How about Microsoft?" → get MSFT price (not "which stock?").
3. Ask "Check my portfolio risk" → get risk data.
4. Ask "What about ESG?" → get compliance report (context: "my portfolio").
5. Send empty message → see graceful error.
6. Refresh page → new session, no carryover (expected).

## Checkpoint Result
_(Fill after deployment.)_
- Commit SHA:
- Ghostfolio URL:
- User Validation: `passed | failed | blocked`
- Notes:

## Observability & Monitoring
- Logs to check:
  - Ghostfolio logs (error classifications, session counts)
- Traces/metrics to check:
  - LangSmith: multi-turn traces (message history growing)
  - LangSmith: error traces with classification metadata
- Alert thresholds:
  - Unclassified errors >5% of requests

## Risks & Edge Cases
- Risk 1: In-memory sessions lost on Railway restart (acceptable for MVP)
- Risk 2: Session store grows unbounded (mitigated: LRU eviction)
- Edge case 1: Concurrent requests to same session_id → race condition
- Edge case 2: Very long conversation (50+ turns) → LLM context overflow
- Edge case 3: Non-English input → agent should still respond

## Eval Coverage (Layer 5 — LangSmith)

This story's functionality is covered by **eval cases 16-20** (Multi-turn and Error Recovery categories) in the LangSmith eval harness (`ghostfolio/apps/api/src/app/agent/evals/dataset.ts`).

### Multi-turn (cases 16-18) — depends on session memory

| Eval Case | Turns | Expected Behavior |
|-----------|-------|-------------------|
| 16 | "Price of AAPL" → "What about MSFT?" | Second turn returns MSFT data |
| 17 | "My portfolio risk" → "Now check ESG" | Tool switches correctly |
| 18 | "Price of AAPL" → "Is that higher than last year?" | Coherent follow-up |

### Error Recovery (cases 19-20) — depends on error handling

| Eval Case | Input | Expected Behavior |
|-----------|-------|-------------------|
| 19 | "" (empty message) | Helpful error, no crash |
| 20 | "Write me a poem about stocks" | Polite decline or redirect |

**Note:** Cases 16-18 will likely show degraded scores until session memory is implemented. Cases 19-20 may partially pass if basic error handling already exists in the agent service (empty input returns error response). The eval harness uses lenient patterns for multi-turn cases to accommodate the stateless agent.

Design doc: `docs/plans/2026-02-24-agent-eval-harness-design.md`

## Implementation Status

**Not yet implemented.** No `memory/` or `errors/` directories exist in `ghostfolio/apps/api/src/app/agent/`. The agent currently treats every message as independent (no session memory) and uses basic try/catch (no classified error handling).

Current behavior without this story:
- Multi-turn: Each message is independent. "What about MSFT?" after asking about AAPL will still work (keyword routing extracts MSFT) but lacks true context awareness.
- Error handling: Basic try/catch in agent.service.ts returns error strings, but no `ErrorType` classification or user-friendly error formatting.

## Notes
- Memory is in-memory only for MVP. Persistent storage is Phase 3.
- Error classification follows implementation strategy: data, tool, model, service.
- Chat UI already exists from US-003; this story only adds error display styling.
- All changes are within `ghostfolio/apps/api/src/app/agent/` — no existing Ghostfolio code modified.
