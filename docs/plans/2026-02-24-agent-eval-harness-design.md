# Agent Eval Harness Design

**Date:** 2026-02-24
**Status:** Approved
**Approach:** LangSmith Eval SDK (pure — no Jest wrapper)

## Problem

The agent has 25 unit tests (Layers 1-2) but zero production eval coverage (Layer 5). We need a reusable eval harness that:
1. Proves MVP requirements (US-007 gate)
2. Survives the transition from keyword routing to LLM-based agent
3. Produces rubric scores (0.0-1.0), not just pass/fail
4. Runs against the live production API

## Architecture

```
Eval Runner (standalone TypeScript script via tsx)
│
├── LangSmith Dataset: "ghostfolio-agent-eval-v1"
│   20+ examples with { input, referenceOutputs }
│
├── Target Function (traceable)
│   HTTP POST → production /api/v1/agent/chat
│   Auth: TEST_SECURITY_TOKEN from env
│
├── Custom Evaluators (rubric scoring 0-1)
│   - toolSelection: correct tool invoked?
│   - dataAccuracy: response contains expected data?
│   - responseQuality: well-formed, no errors?
│   - noHallucination: numbers trace to tool output?
│
├── Summary Evaluator
│   - overallPassRate: % of cases scoring > 0.7
│   - CI gate: assert >= 80% pass rate
│
└── Results → LangSmith dashboard (experiment comparison)
```

## Design Decisions

### Why LangSmith (not custom runner or Promptfoo)
- Already have `LANGSMITH_API_KEY` in Railway production
- Dashboard gives experiment comparison across runs for free
- LLM-as-judge evaluators available when LLM agent ships
- Dataset management built in (versioning, cloning)
- `traceable()` wraps the HTTP target function for end-to-end trace visibility

### Why standalone script (not Jest)
- Eval runs are not unit tests — they hit production, take longer, score on a rubric
- No need for Jest lifecycle, mocking, or assertion library
- Run via `npx tsx` — simpler, no test runner overhead
- LangSmith dashboard is the report, not Jest output

### Why rubric scoring (not pass/fail)
- Current keyword router is deterministic, but LLM agent will be non-deterministic
- Rubric scores (0.0-1.0) let you set thresholds that tolerate variation
- Multiple criteria per case (tool selection, data accuracy, response quality) give granular signal
- Summary evaluator aggregates into a single pass rate for gating

## Eval Dataset: "ghostfolio-agent-eval-v1" (20 cases)

### Market Data (5 cases)

| # | Input | Expected Tool | Key Assertions |
|---|-------|--------------|----------------|
| 1 | "What's the current price of AAPL?" | `market_data_fetch` | Contains AAPL, price > 0 |
| 2 | "Compare MSFT and GOOGL prices" | `market_data_fetch` | Contains both MSFT and GOOGL |
| 3 | "What's the PE ratio of TSLA?" | `market_data_fetch` | Contains TSLA data |
| 4 | "Price of BTC-USD" | `market_data_fetch` | Handles crypto (error or data) |
| 5 | "Price of INVALIDXYZ" | `market_data_fetch` | Graceful error, no crash |

### Portfolio Analysis (5 cases)

| # | Input | Expected Tool | Key Assertions |
|---|-------|--------------|----------------|
| 6 | "What's my portfolio risk?" | `portfolio_risk_analysis` | HHI, concentration level |
| 7 | "Show my asset allocation" | `portfolio_risk_analysis` | Allocation breakdown |
| 8 | "How concentrated is my portfolio?" | `portfolio_risk_analysis` | Concentration %, top holding |
| 9 | "How has my portfolio performed?" | `portfolio_risk_analysis` | Return %, total value |
| 10 | "Am I diversified enough?" | `portfolio_risk_analysis` | Diversification assessment |

### Compliance (5 cases)

| # | Input | Expected Tool | Key Assertions |
|---|-------|--------------|----------------|
| 11 | "Run an ESG compliance check" | `compliance_check` | Score, violations with XOM |
| 12 | "Check for fossil fuel exposure" | `compliance_check` | Category filter, XOM flagged |
| 13 | "Are my holdings ethical?" | `compliance_check` | Score + clean/flagged breakdown |
| 14 | "Any weapons companies in portfolio?" | `compliance_check` | Category filter for weapons |
| 15 | "Give me my compliance score" | `compliance_check` | Numeric score 0-100 |

### Multi-turn (3 cases)

| # | Turns | Expected Behavior |
|---|-------|-------------------|
| 16 | "Price of AAPL" → "What about MSFT?" | Second turn returns MSFT data |
| 17 | "My portfolio risk" → "Now check ESG" | Tool switches correctly |
| 18 | "Price of AAPL" → "Is that higher than last year?" | Coherent follow-up |

### Error Recovery (2 cases)

| # | Input | Expected Behavior |
|---|-------|-------------------|
| 19 | "" (empty message) | Helpful error, no crash |
| 20 | "Write me a poem about stocks" | Polite decline or redirect |

## Evaluators (Rubric Scoring)

### Row-level evaluators

Each returns `{ key: string, score: number }` where `score` is 0.0-1.0.

#### `toolSelection`
- **Score 1.0**: `tool_calls[0].name` matches `referenceOutputs.expectedTool`
- **Score 0.0**: Wrong tool or no tool call
- **Future**: When LLM routes, this catches routing regressions

#### `dataAccuracy`
- **Score 1.0**: All expected patterns from `referenceOutputs.expectedPatterns` found in response
- **Score 0.5**: Some patterns found
- **Score 0.0**: No patterns found
- **Patterns**: Regex or substring checks (e.g., `/AAPL/`, `/\$\d+/`)

#### `responseQuality`
- **Score 1.0**: Non-empty, no stack traces, no "undefined", reasonable length (10-5000 chars)
- **Score 0.5**: Response present but contains error indicators
- **Score 0.0**: Empty, error stack trace, or nonsensical

#### `noHallucination`
- **Score 1.0**: All numbers in response appear in tool_calls output
- **Score 0.0**: Response contains numbers not traceable to tool output
- **Note**: Most valuable when LLM generates free-text responses. For keyword router, this is effectively always 1.0.

### Summary evaluator

#### `overallPassRate`
- Computes: (cases where average rubric score > 0.7) / total cases
- Gate: Asserts >= 80% pass rate
- Logs: per-category breakdown (market, portfolio, compliance, multi-turn, error)

## File Structure

```
ghostfolio/apps/api/src/app/agent/evals/
├── eval-runner.ts          # Main: seed dataset + run evaluate()
├── target.ts               # traceable() HTTP wrapper → production
├── evaluators/
│   ├── tool-selection.ts   # Correct tool invoked?
│   ├── data-accuracy.ts    # Expected data present?
│   ├── response-quality.ts # Well-formed response?
│   └── no-hallucination.ts # Numbers trace to tool output?
├── dataset.ts              # 20 eval cases as TS objects
└── README.md               # How to run evals
```

## Run Command

```bash
cd ghostfolio

# Set required env vars
export LANGSMITH_API_KEY=<your-key>
export TEST_SECURITY_TOKEN=<token-from-.env>
export EVAL_BASE_URL=https://ghostfolio-production-e8d1.up.railway.app

# Run evals
npx tsx apps/api/src/app/agent/evals/eval-runner.ts
```

Results appear in LangSmith dashboard under experiment "ghostfolio-agent-eval".

## Dependencies

```
langsmith         # LangSmith SDK (evaluate, Client, traceable)
```

Already available: `LANGSMITH_API_KEY` in Railway env vars.

## Future Extensions

1. **LLM-as-judge evaluator**: When LLM agent ships, add an evaluator that uses Claude to judge response quality (LangSmith supports this natively)
2. **Dataset versioning**: Clone dataset before modifying, compare experiments across dataset versions
3. **Regression detection**: Compare current experiment scores to baseline, fail CI if any category drops > 10%
4. **50-case dataset**: Phase 3 expansion from 20 → 50 cases per US-007 notes
5. **Adversarial cases**: Prompt injection, jailbreak attempts, XSS in user input

## Relationship to Existing Test Layers

| Layer | Tool | Purpose | Runs when |
|-------|------|---------|-----------|
| 1: Unit | Jest | Tool logic correctness | Every commit |
| 2: Integration | Jest | NestJS DI wiring | Every commit |
| 3: Behavioral | Jest | Agent routing (mocked) | Every commit |
| 4: Contract | Jest | API shape stability | Every commit |
| **5: Eval** | **LangSmith** | **Production correctness** | **Pre-deploy gate** |

Layers 1-4 remain in Jest. Layer 5 is the LangSmith eval harness — separate tool, separate cadence, separate reporting.
