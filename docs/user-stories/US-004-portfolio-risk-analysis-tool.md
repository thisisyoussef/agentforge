# US-004: Portfolio Risk Analysis Tool (Ghostfolio Service Integration)

## Status
- State: `done`
- Owner: `youssef`
- Depends on: US-002, US-003
- Related PR/Commit: ghostfolio `375e6f1` (implement), `f54d58a` (auth fix)
- Target environment: `prod`

## Persona
**Sam, the End User** wants to understand portfolio concentration, allocation, and performance without manually crunching numbers.

**Alex, the Agent Developer** wants to prove the agent can access Ghostfolio services directly (NestJS DI) and compute domain-specific metrics.

## User Story
> As Sam, I want to ask about my portfolio's risk profile so that I understand concentration, allocation, and performance in plain language.

## Goal
Add the second tool (`portfolio_risk_analysis`) that accesses Ghostfolio's portfolio services directly via NestJS dependency injection, computes risk metrics (concentration, HHI, allocation breakdown, performance), and returns structured results through the existing agent and chat UI.

## Scope
In scope:
1. `ghostfolio/apps/api/src/app/agent/tools/portfolio-analysis.tool.ts` — tool implementation.
2. Direct service injection from Ghostfolio's existing `PortfolioService` (or internal HTTP calls as fallback).
3. Ghostfolio data access: portfolio details, performance, holdings.
4. Risk computations: top holding %, HHI, asset class allocation, performance summary.
5. Register tool in LangGraph graph.
6. Three eval test cases.

Out of scope:
1. Advanced volatility models (Monte Carlo, VaR).
2. Historical backtesting.
3. Sharpe ratio (needs risk-free rate data).
4. Rebalancing recommendations.

## Pre-Implementation Audit
Local sources to read before writing any code:
1. `ghostfolio/apps/api/src/app/portfolio/portfolio.service.ts` — service to inject directly
2. `ghostfolio/apps/api/src/app/portfolio/portfolio.controller.ts` — API endpoints (fallback approach)
3. `ghostfolio/apps/api/src/app/agent/agent.service.ts` — existing graph to extend with new tool
4. `ghostfolio/apps/api/src/app/agent/tools/market-data.tool.ts` — tool pattern to follow
5. `ghostfolio/apps/api/src/app/agent/agent.module.ts` — module imports for DI

## Preparation Phase (Mandatory)
1. Read local code listed above — especially the PortfolioService to understand available methods.
2. Web-check relevant docs:
   - HHI (Herfindahl-Hirschman Index) calculation formula
   - LangGraph tool registration pattern (JS/TS)
   - NestJS dependency injection patterns
3. Write Preparation Notes.

### Preparation Notes
_(Fill during execution.)_

Local docs/code reviewed:
1.
2.

Expected data access approaches:
```typescript
// Approach 1: Direct service injection (preferred)
// Import PortfolioModule into AgentModule → inject PortfolioService
// this.portfolioService.getDetails(...)

// Approach 2: Internal HTTP calls (fallback)
// GET /api/v1/portfolio/holdings with bearer token
// GET /api/v1/portfolio/details
// GET /api/v1/portfolio/performance?range=1y
```

Expected data shapes:
```typescript
// Holdings: { symbol, name, allocationCurrent, marketPrice, value, ... }
// Details: { holdings: { [symbol]: { allocationCurrent, sectors, value, ... } } }
// Performance: { chart: [...], performance: { currentValue, totalReturn, ... } }
```

HHI formula:
```
HHI = Σ(allocation_i²) where allocation_i is fraction (0-1)
HHI range: 0 (perfectly diversified) to 1 (single holding)
```

Planned failing tests:
1. `test concentration calculation — correct top holding % and HHI for known input`
2. `test allocation breakdown — correct asset class grouping`
3. `test agent routes portfolio question — chat endpoint routes to portfolio_risk_analysis`
4. `test graceful error when portfolio data unavailable`

## UX Script
Happy path:
1. User opens Ghostfolio `/agent` page (already exists from US-003).
2. User types "What's my portfolio concentration risk?"
3. Agent calls `portfolio_risk_analysis` tool → accesses Ghostfolio data.
4. Response shows top holding, HHI, allocation breakdown in natural language.

Error path:
1. Portfolio data unavailable (e.g., no holdings seeded).
2. Agent responds: "I'm unable to access portfolio data right now. Please try again later."
3. Other tools (market_data_fetch) still work.

## Preconditions
- [ ] US-002 complete (Ghostfolio running with ≥5 seeded holdings)
- [ ] US-003 complete (LangGraph agent + Angular chat page exist)

## TDD Plan
Write tests first. Red → Green → Refactor.

### Test files to create/modify
1. `ghostfolio/apps/api/src/app/agent/tools/portfolio-analysis.tool.spec.ts`
   - `should calculate correct concentration for single holding (100%, HHI=1.0)`
   - `should calculate correct HHI for equal three holdings (≈0.33)`
   - `should group holdings by asset class correctly`
   - `should handle empty portfolio gracefully`
2. `ghostfolio/apps/api/src/app/agent/agent.controller.spec.ts` (extend)
   - `should route portfolio risk question to portfolio_risk_analysis tool`

### Red → Green → Refactor sequence
1. Create test files with all tests. Run `npx nx test api --testPathPattern=agent` — all fail (red).
2. Implement `portfolio-analysis.tool.ts` → concentration/allocation tests go green.
3. Register tool in graph → routing test goes green.
4. Refactor: extract shared helpers if needed.

## Step-by-step Implementation Plan
1. Import `PortfolioModule` into `AgentModule` (or configure HTTP fallback).
2. Create `ghostfolio/apps/api/src/app/agent/tools/portfolio-analysis.tool.ts`:
   - `PortfolioAnalysisInput`: `dateRange?: string`, `metrics?: string[]`.
   - `PortfolioAnalysisOutput`: `concentration`, `allocation`, `performance`, `riskMetrics`.
   - Access holdings/details/performance from Ghostfolio.
   - Compute concentration (top holding %, HHI).
   - Compute allocation (group by asset class).
   - Compute performance summary.
3. Register tool in `agent.service.ts` LangGraph graph.
4. Deploy (single Ghostfolio service) and test via chat UI.

## Implementation Details

Implemented files:
1. `ghostfolio/apps/api/src/app/agent/tools/portfolio-analysis.tool.ts` — tool with HHI, concentration, allocation, performance metrics
2. `ghostfolio/apps/api/src/app/agent/tools/portfolio-analysis.tool.spec.ts` — 10 unit tests
3. `ghostfolio/apps/api/src/app/agent/agent.service.ts` — extended with portfolio keyword routing + `handlePortfolioQuestion()`
4. `ghostfolio/apps/api/src/app/agent/agent.controller.spec.ts` — added portfolio routing test

Key interfaces:
```typescript
export interface PortfolioAnalysisOutput {
  concentration: {
    topHolding: { symbol: string; name: string; percentage: number };
    topFiveHoldings: Array<{ symbol: string; name: string; percentage: number }>;
    hhi: number;
    concentrationLevel: string; // 'Highly Concentrated' | 'Moderately Concentrated' | 'Moderately Diversified' | 'Well Diversified'
  };
  allocation: Record<string, { count: number; totalPercentage: number; holdings: string[] }>;
  performance: { currentValue: number; totalReturn: number; totalReturnPercent: number; totalInvestment: number };
  holdingsCount: number;
}
```

Data access: Direct NestJS DI injection of `PortfolioService.getDetails()` and `PortfolioService.getPerformance()`. Uses JWT-authenticated `userId` parameter.

## Acceptance Criteria
- [ ] AC1: Agent routes portfolio risk questions to `portfolio_risk_analysis`.
- [ ] AC2: Tool returns structured data from live Ghostfolio (not mocked).
- [ ] AC3: Agent synthesizes risk data into readable response.
- [ ] AC4: All TDD test cases pass.
- [ ] AC5: Graceful error if portfolio data unavailable.

## Local Validation
```bash
# Tests (story-specific)
cd ghostfolio && npx nx test api --testPathPattern=portfolio-analysis

# Full API test suite
npx nx test api

# Build
npx nx build api
```

## Deployment Handoff (Mandatory)
1. Commit changes in `ghostfolio/`.
2. Push to `main` → Railway auto-deploys Ghostfolio.
3. Verify health endpoint.
4. Test via chat UI at `/agent`.
5. Record in Checkpoint Result.

## How To Verify In Prod (Required)
- Production URL(s):
  - Ghostfolio: `https://ghostfolio-production-e8d1.up.railway.app`
  - Chat page: `https://ghostfolio-production-e8d1.up.railway.app/agent`
- Expected results:
  - Ask "What's my portfolio concentration risk?" → response shows top holding %, HHI, allocation
  - Data reflects seeded portfolio (AAPL, MSFT, GOOGL, BND, VWO, BTC, XOM)
  - `tool_calls` includes `portfolio_risk_analysis`
- Failure signals:
  - "Unable to access portfolio" error
  - 500 from API
  - Missing tool call in response
- Rollback action:
  - Revert Ghostfolio deployment; market_data_fetch still works

## User Checkpoint Test
1. Open Ghostfolio `/agent` → ask "What's my portfolio concentration risk?" → see metrics.
2. Ask "Show my asset allocation" → see breakdown by asset class.
3. Ask "How has my portfolio performed?" → see performance data.
4. Verify data matches seeded portfolio.

## Checkpoint Result
- Commit SHA: ghostfolio `375e6f1` (implement), `f54d58a` (auth fix)
- Ghostfolio URL: `https://ghostfolio-production-e8d1.up.railway.app`
- Agent chat page: `https://ghostfolio-production-e8d1.up.railway.app/en/agent`
- User Validation: `passed`
- Notes:
  - 10/10 unit tests passing
  - Portfolio data accessed via NestJS DI (PortfolioService injection)
  - HHI, concentration, allocation, and performance metrics all computed correctly
  - Auth fixed to use JWT userId instead of PrismaService lookup
  - Keyword routing: 11 portfolio-related keywords trigger this tool

## Observability & Monitoring
- Logs to check:
  - Railway Ghostfolio logs (portfolio service calls, timing)
- Traces/metrics to check:
  - LangSmith: `portfolio_risk_analysis` latency and success rate
- Alert thresholds:
  - Portfolio data fetch >5s, tool failure >10%

## Risks & Edge Cases
- Risk 1: Ghostfolio internal service API differs from controller API (undocumented)
- Risk 2: NestJS DI circular dependency between AgentModule and PortfolioModule
- Risk 3: Seeded portfolio data insufficient for meaningful metrics
- Edge case 1: Single holding portfolio (concentration = 100%)
- Edge case 2: Empty portfolio (no holdings)
- Edge case 3: Holdings with missing asset class metadata

## Eval Coverage (Layer 5 — LangSmith)

This story's functionality is covered by **eval cases 6-10** (Portfolio Analysis category) in the LangSmith eval harness (`ghostfolio/apps/api/src/app/agent/evals/dataset.ts`).

| Eval Case | Input | Expected Tool | Key Assertions |
|-----------|-------|---------------|----------------|
| 6 | "What's my portfolio risk?" | `portfolio_risk_analysis` | HHI, concentration level |
| 7 | "Show my asset allocation" | `portfolio_risk_analysis` | Allocation breakdown |
| 8 | "How concentrated is my portfolio?" | `portfolio_risk_analysis` | Concentration %, top holding |
| 9 | "How has my portfolio performed?" | `portfolio_risk_analysis` | Return %, total value |
| 10 | "Am I diversified enough?" | `portfolio_risk_analysis` | Diversification assessment |

Design doc: `docs/plans/2026-02-24-agent-eval-harness-design.md`

## Notes
- **Key advantage of Approach A**: Agent can inject Ghostfolio services directly via NestJS DI, no HTTP overhead.
- If DI proves complex, fall back to internal HTTP calls (still within same process).
- Can be developed in parallel with US-005 since both share the same prerequisites.
- Ghostfolio service reference: `ghostfolio/apps/api/src/app/portfolio/portfolio.service.ts`
