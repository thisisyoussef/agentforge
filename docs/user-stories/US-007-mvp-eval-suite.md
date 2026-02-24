# US-007: MVP Eval Suite and Production Gate

## Status
- State: `in-progress`
- Owner: `youssef`
- Depends on: US-006
- Related PR/Commit:
- Target environment: `prod`
- Design doc: `docs/plans/2026-02-24-agent-eval-harness-design.md`
- Implementation plan: `docs/plans/2026-02-24-agent-eval-harness-impl.md`

## Persona
**Alex, the Agent Developer** wants documented proof that all 9 MVP requirements are met so the gate is passed with evidence.

## User Story
> As Alex, I want a consolidated eval suite and MVP evidence document so that I can prove all requirements are met.

## Goal
Build a **reusable eval harness using LangSmith** that scores the Ghostfolio agent across 20 test cases with rubric-based scoring (0-1). Run it against production, record results in the LangSmith dashboard, and create an MVP evidence document mapping each requirement to its proof.

## Approach: LangSmith Eval SDK (not Jest)

The eval suite is a **standalone TypeScript script** (`eval-runner.ts`) run via `npx tsx`, NOT a Jest test file. This is intentional:
- Evals hit production (slow, non-deterministic) — different cadence from unit tests
- Rubric scoring (0-1) replaces pass/fail — future-proof for LLM agent
- LangSmith dashboard is the report, not Jest output
- Dataset lives in LangSmith, seeded from TypeScript definitions

## Scope
In scope:
1. `ghostfolio/apps/api/src/app/agent/evals/` — full eval harness directory:
   - `types.ts` — shared types (EvalCase, EvalInput, EvalReferenceOutput, AgentChatResponse)
   - `dataset.ts` — 20 eval cases across 5 categories
   - `target.ts` — `traceable()` HTTP wrapper hitting production agent API
   - `evaluators/` — 4 rubric-scoring evaluators + barrel export
   - `eval-runner.ts` — main script: seed dataset + run `evaluate()`
   - `README.md` — quickstart and reference
2. LangSmith dataset: `ghostfolio-agent-eval-v1` (20 cases)
3. LangSmith experiment: `ghostfolio-agent-eval` (scored results)
4. MVP evidence document (`docs/user-stories/MVP-EVIDENCE.md`)
5. Update all story statuses to `done`

Out of scope:
1. 50-case dataset (Phase 3).
2. Adversarial testing.
3. LLM-as-judge evaluation (future extension when LLM agent ships).
4. Performance benchmarking.

## Pre-Implementation Audit
Local sources to read before writing any code:
1. `ghostfolio/apps/api/src/app/agent/agent.service.ts` — keyword routing, tool invocation, response building
2. `ghostfolio/apps/api/src/app/agent/agent.controller.ts` — HTTP endpoint shape (ChatRequestDto/ChatResponseDto)
3. `ghostfolio/apps/api/src/app/agent/tools/*.ts` — all 3 tool implementations
4. `ghostfolio/apps/api/src/app/agent/tools/*.spec.ts` — existing unit test patterns
5. `docs/plans/2026-02-24-agent-eval-harness-design.md` — approved design doc

## Eval Dataset: 20 cases across 5 categories

| Category | Count | Example input | Expected tool | Source Story |
|----------|-------|---------------|---------------|--------------|
| Market Data | 5 | "Price of AAPL" | `market_data_fetch` | US-003 |
| Portfolio Analysis | 5 | "What's my portfolio risk?" | `portfolio_risk_analysis` | US-004 |
| Compliance | 5 | "Run an ESG compliance check" | `compliance_check` | US-005 |
| Multi-turn | 3 | Turn 1 → Turn 2 (context) | varies | US-006 |
| Error Recovery | 2 | "" / "Write me a poem" | null (no tool) | US-006 |

## Evaluators (Rubric Scoring 0-1)

| Evaluator | What it scores | 1.0 means | 0.0 means |
|-----------|---------------|-----------|-----------|
| `tool_selection` | Correct tool invoked | Right tool called | Wrong or no tool |
| `data_accuracy` | Expected patterns in response | All patterns found | No patterns found |
| `response_quality` | Well-formed response | No errors, good length | Empty or HTTP error |
| `no_hallucination` | Numbers trace to tool output | All traceable | Fabricated numbers |
| `overall_pass_rate` (summary) | Aggregate gate | ≥80% cases pass | <80% |

## TDD Plan
This story builds the eval harness itself — it IS the test artifact.

### Implementation tasks (from impl plan)
1. Install `langsmith` dependency
2. Create types + 20-case dataset definition
3. Create traceable target function (HTTP POST to production)
4. Create 4 rubric-scoring evaluators
5. Create eval runner (`evaluate()` + dataset seeding)
6. Create README
7. End-to-end run against production (≥80% pass rate)
8. Fix any failing cases (contingency)

### Validation sequence
1. All files compile via `npx tsx`
2. Eval runner seeds dataset in LangSmith (20 cases)
3. Eval runs against production → ≥80% pass rate
4. Results visible in LangSmith dashboard
5. Document results in MVP-EVIDENCE.md

## Acceptance Criteria
- [ ] AC1: Eval suite contains 20 test cases with rubric-scored expected outcomes.
- [ ] AC2: Suite runs against production via `npx tsx` and produces scored results.
- [ ] AC3: Overall pass rate ≥80% (summary evaluator).
- [ ] AC4: Each of 9 MVP requirements has documented evidence.
- [ ] AC5: LangSmith dashboard shows experiment with per-evaluator scores.
- [ ] AC6: All story statuses updated.

## Local Validation
```bash
# Run eval suite against production (NOT Jest — standalone tsx script)
cd ghostfolio
LANGSMITH_API_KEY=$LANGSMITH_API_KEY \
EVAL_BASE_URL=https://ghostfolio-production-e8d1.up.railway.app \
npx tsx apps/api/src/app/agent/evals/eval-runner.ts

# Layers 1-4 should still pass (Jest)
npx dotenv-cli -e .env.example -- npx nx test api --testPathPattern="app/agent/"
```

## Deployment Handoff (Mandatory)
1. Commit eval harness and MVP-EVIDENCE.md.
2. Push to `main`.
3. Record LangSmith experiment URL and pass rate in Checkpoint Result.

## How To Verify In Prod (Required)
- Production URL(s):
  - Ghostfolio: `https://ghostfolio-production-e8d1.up.railway.app`
  - Chat page: `https://ghostfolio-production-e8d1.up.railway.app/agent`
  - LangSmith dashboard: `https://smith.langchain.com/`
- Expected results:
  - Eval suite ≥80% pass rate on production
  - Each MVP requirement has evidence
  - LangSmith experiment shows all 20 cases with rubric scores
  - Chat UI works for all manual scenarios
- Failure signals:
  - Pass rate <80%
  - Any MVP requirement has zero evidence
  - LangSmith experiment missing or incomplete
- Rollback action:
  - N/A (eval is read-only; fix failing tests by fixing underlying issues)

## User Checkpoint Test
1. Run `npx tsx apps/api/src/app/agent/evals/eval-runner.ts` against prod → see pass rate.
2. Open LangSmith dashboard → verify experiment `ghostfolio-agent-eval-*` with 20 cases.
3. Open Ghostfolio `/agent` → manually run 3 verification scenarios.
4. Read MVP-EVIDENCE.md → all 9 requirements have evidence.

## Checkpoint Result
_(Fill after deployment.)_
- Commit SHA:
- Ghostfolio URL:
- LangSmith experiment URL:
- Eval pass rate:
- User Validation: `passed | failed | blocked`
- Notes:

## Observability & Monitoring
- Logs to check:
  - Eval runner stdout (pass rate, category breakdown)
  - Railway Ghostfolio logs during eval
- Traces/metrics to check:
  - LangSmith: all traces from eval run (via `traceable()` target function)
  - LangSmith: per-evaluator scores and summary
  - LangSmith: latency and token usage
- Alert thresholds:
  - N/A (one-time validation, becomes recurring pre-deploy gate)

## Risks & Edge Cases
- Risk 1: Flaky results from Yahoo Finance API instability (mitigate: `data_accuracy` uses regex patterns, not exact values)
- Risk 2: Rate limiting from repeated eval runs against production (mitigate: `maxConcurrency: 2`)
- Risk 3: Multi-turn cases may fail because agent is currently stateless (mitigate: lenient patterns for multi-turn category)
- Edge case 1: Production env differs from local (eval always hits production, no local mode)
- Edge case 2: LangSmith API rate limits during dataset seeding

## Notes
- This is the final MVP gate story. Once it passes, MVP is complete.
- Eval suite uses **LangSmith evaluate() API**, not Jest. This is a deliberate separation.
- Rubric scoring (0-1) replaces pass/fail to handle future LLM non-determinism.
- Eval suite becomes the foundation for 50-case dataset in Phase 3.
- Design doc: `docs/plans/2026-02-24-agent-eval-harness-design.md`
- Implementation plan: `docs/plans/2026-02-24-agent-eval-harness-impl.md`

## MVP Requirements Checklist
_(Fill during execution.)_
| # | Requirement | Evidence | Status |
|---|------------|----------|--------|
| 1 | Agent responds to NL queries | | |
| 2 | ≥3 functional tools | | |
| 3 | Tools return structured results | | |
| 4 | Agent synthesizes results | | |
| 5 | Conversation history | | |
| 6 | Basic error handling | | |
| 7 | Domain verification check | | |
| 8 | 5+ test cases | | |
| 9 | Deployed + accessible | | |
