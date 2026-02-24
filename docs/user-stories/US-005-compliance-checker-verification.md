# US-005: ESG Compliance Checker with Domain Verification

## Status
- State: `done`
- Owner: `youssef`
- Depends on: US-002, US-003
- Related PR/Commit: ghostfolio `a379807` (implement + webpack fix), `0c18f95` (name-based matching)
- Target environment: `prod`

## Persona
**Sam, the Ethical Investor** wants to know if portfolio holdings violate ESG criteria so they can make informed decisions.

**Alex, the Agent Developer** wants a domain-specific verification check (MVP requirement #7) that proves claims are backed by data, not hallucinated.

## User Story
> As Sam, I want to check if my holdings comply with ESG criteria so that I can identify and address potential violations.
> As Alex, I want a verification tool that cross-references portfolio data against an authoritative dataset so I can demonstrate domain-specific verification.

## Goal
Add the third tool (`compliance_check`) that accesses Ghostfolio portfolio holdings (via service injection or internal API), cross-references them against a static ESG violations dataset, and returns structured violations with categories, severities, and a compliance score. This tool IS the domain-specific verification check (MVP requirement #7).

## Scope
In scope:
1. `ghostfolio/apps/api/src/app/agent/tools/compliance-checker.tool.ts` — tool implementation.
2. `ghostfolio/apps/api/src/app/agent/data/esg-violations.json` — static dataset (20-30 tickers).
3. ESG categories: `fossil_fuels`, `weapons_defense`, `tobacco`, `gambling`, `controversial_labor`.
4. Compliance score: `(cleanPortfolioValue / totalPortfolioValue) * 100`.
5. Optional category filter (e.g., "only fossil fuels").
6. Register tool in LangGraph graph.
7. Two eval test cases.

Out of scope:
1. Live ESG data feeds (MSCI, Sustainalytics).
2. Custom user-defined compliance rules.
3. Industry-standard ESG scoring methodology.

## Pre-Implementation Audit
Local sources to read before writing any code:
1. `ghostfolio/apps/api/src/app/portfolio/portfolio.service.ts` — service for holdings access
2. `ghostfolio/apps/api/src/app/agent/tools/market-data.tool.ts` — tool pattern to follow
3. `ghostfolio/apps/api/src/app/agent/tools/portfolio-analysis.tool.ts` — Ghostfolio data access pattern (created in US-004)
4. `ghostfolio/apps/api/src/app/agent/agent.service.ts` — graph to extend with third tool

## Preparation Phase (Mandatory)
1. Read local code listed above.
2. Web-check relevant docs:
   - Common ESG exclusion categories and well-known violators
   - JSON schema design for the violations dataset
3. Write Preparation Notes.

### Preparation Notes
_(Fill during execution.)_

Local docs/code reviewed:
1.
2.

ESG violations dataset design:
```json
{
  "version": "1.0",
  "lastUpdated": "2026-02-24",
  "violations": [
    {"symbol": "XOM", "name": "Exxon Mobil", "categories": ["fossil_fuels"], "severity": "high", "reason": "Major oil and gas producer"},
    {"symbol": "CVX", "name": "Chevron", "categories": ["fossil_fuels"], "severity": "high", "reason": "Integrated energy company"},
    {"symbol": "LMT", "name": "Lockheed Martin", "categories": ["weapons_defense"], "severity": "high", "reason": "Defense contractor"},
    {"symbol": "PM", "name": "Philip Morris", "categories": ["tobacco"], "severity": "high", "reason": "Tobacco manufacturer"}
  ]
}
```

Compliance score formula:
```
cleanValue = sum(value for holding if symbol NOT in violations)
totalValue = sum(all holding values)
score = (cleanValue / totalValue) * 100
```

Planned failing tests:
1. `should return score = 100 for portfolio with no flagged tickers`
2. `should flag XOM as fossil_fuels violation with severity high`
3. `should filter by category when requested`
4. `should calculate correct compliance score for known values`
5. `should route ESG question to compliance_check tool`

## UX Script
Happy path:
1. User types "Is my portfolio ESG compliant?" in Ghostfolio `/agent` chat.
2. Agent calls `compliance_check` → accesses holdings → cross-references ESG dataset.
3. Response shows compliance score, violations list, and clean holdings.
4. User asks "Do I hold any fossil fuel companies?" → filtered result.

Error path:
1. Portfolio data unavailable.
2. Agent responds: "Unable to check portfolio compliance — portfolio service unavailable."
3. Other tools still work.

## Preconditions
- [ ] US-002 complete (Ghostfolio with seeded portfolio including XOM)
- [ ] US-003 complete (LangGraph agent + Angular chat page exist)
- [ ] Portfolio data access pattern established (from US-004 or independently)

## TDD Plan
Write tests first. Red → Green → Refactor.

### Test files to create/modify
1. `ghostfolio/apps/api/src/app/agent/tools/compliance-checker.tool.spec.ts`
   - `should return score 100 for all-clean portfolio`
   - `should flag XOM with category fossil_fuels and severity high`
   - `should calculate correct compliance score (70% clean → score = 70.0)`
   - `should filter by category (fossil_fuels only)`
   - `should handle empty portfolio gracefully`
2. `ghostfolio/apps/api/src/app/agent/agent.controller.spec.ts` (extend)
   - `should route ESG compliance question to compliance_check tool`

### Red → Green → Refactor sequence
1. Create ESG dataset file first (test fixture).
2. Write all tests. Run `npx nx test api --testPathPattern=agent` — all fail (red).
3. Implement `compliance-checker.tool.ts` → unit tests go green.
4. Register tool in graph → routing test goes green.
5. Refactor: extract shared patterns if any.

## Step-by-step Implementation Plan
1. Create `ghostfolio/apps/api/src/app/agent/data/esg-violations.json` with 20-30 entries.
2. Create `ghostfolio/apps/api/src/app/agent/tools/compliance-checker.tool.ts`:
   - `ComplianceCheckInput`: `filterCategory?: string`.
   - `ComplianceCheckOutput`: `complianceScore`, `violations`, `cleanHoldings`, `totalChecked`.
   - Load ESG dataset, access holdings from Ghostfolio, cross-reference, compute score.
3. Register tool in `agent.service.ts` LangGraph graph.
4. Deploy (single Ghostfolio service) and test via chat UI.

## Implementation Details

Implemented files:
1. `ghostfolio/apps/api/src/app/agent/tools/compliance-checker.tool.ts` — tool with ESG cross-referencing, compliance scoring, category filtering
2. `ghostfolio/apps/api/src/app/agent/tools/compliance-checker.tool.spec.ts` — 9 unit tests
3. `ghostfolio/apps/api/src/app/agent/data/esg-violations.json` — 25-company ESG violations dataset (5 categories)
4. `ghostfolio/apps/api/src/app/agent/agent.service.ts` — extended with ESG keyword routing + `handleComplianceQuestion()` + category detection
5. `ghostfolio/apps/api/src/app/agent/agent.controller.spec.ts` — added ESG routing test

Key interfaces:
```typescript
export interface ComplianceCheckOutput {
  complianceScore: number; // 0-100, (cleanValue/totalValue)*100
  violations: Array<{
    symbol: string; name: string; categories: string[];
    severity: string; reason: string; portfolioPercentage: number;
  }>;
  cleanHoldings: Array<{ symbol: string; name: string; portfolioPercentage: number }>;
  totalChecked: number;
  datasetVersion: string;
  lastUpdated: string;
}
```

Data access: Portfolio holdings via `PortfolioService.getDetails()` (same pattern as US-004). ESG violations loaded from static JSON at module init. Supports name-based matching for MANUAL data source holdings (UUID symbols).

## Acceptance Criteria
- [ ] AC1: Agent routes ESG/compliance questions to `compliance_check`.
- [ ] AC2: Cross-references real Ghostfolio holdings against ESG dataset.
- [ ] AC3: Violations include category, severity, source attribution (dataset version).
- [ ] AC4: Compliance score mathematically correct (verified by test).
- [ ] AC5: All TDD test cases pass.
- [ ] AC6: XOM flagged as `fossil_fuels` violation in seeded portfolio.

## Local Validation
```bash
# Tests (story-specific)
cd ghostfolio && npx nx test api --testPathPattern=compliance

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
  - "Is my portfolio ESG compliant?" → compliance score, XOM flagged as fossil_fuels
  - "Do I hold fossil fuel companies?" → filtered result showing XOM
  - Source attribution mentions ESG dataset version
- Failure signals:
  - "Unable to check compliance" error
  - XOM not flagged (dataset or matching issue)
  - Score doesn't add up
- Rollback action:
  - Revert Ghostfolio deployment; other tools unaffected

## User Checkpoint Test
1. Ask "Is my portfolio ESG compliant?" → see score and XOM violation.
2. Ask "Do I hold fossil fuel companies?" → see XOM only.
3. Verify compliance score math matches portfolio allocation.
4. Verify source attribution shows dataset version/date.

## Checkpoint Result
- Commit SHA: ghostfolio `a379807` (implement + webpack fix), `0c18f95` (name-based matching)
- Ghostfolio URL: `https://ghostfolio-production-e8d1.up.railway.app`
- Agent chat page: `https://ghostfolio-production-e8d1.up.railway.app/en/agent`
- User Validation: `passed`
- Notes:
  - 9 unit tests passing (+ 1 controller routing test)
  - ESG dataset: 25 companies across 5 categories (fossil_fuels, weapons_defense, tobacco, gambling, controversial_labor)
  - XOM correctly flagged as fossil_fuels violation in seeded portfolio
  - Name-based matching added for MANUAL data source holdings (BTC has UUID symbol)
  - Category filter works: "Do I hold fossil fuel companies?" → filters to fossil_fuels only
  - Webpack JSON loading fix applied for production build

## Observability & Monitoring
- Logs to check:
  - Ghostfolio logs (ESG dataset load, portfolio data access)
- Traces/metrics to check:
  - LangSmith: `compliance_check` latency and success rate
- Alert thresholds:
  - Tool failure >10%

## Risks & Edge Cases
- Risk 1: Seeded portfolio has no ESG-flagged holdings (mitigated: XOM in seed)
- Risk 2: ESG dataset too small to be meaningful
- Edge case 1: Empty portfolio → "no holdings to check"
- Edge case 2: All holdings flagged → score = 0%
- Edge case 3: Category filter with no matches → "no violations in this category"

## Eval Coverage (Layer 5 — LangSmith)

This story's functionality is covered by **eval cases 11-15** (Compliance category) in the LangSmith eval harness (`ghostfolio/apps/api/src/app/agent/evals/dataset.ts`).

| Eval Case | Input | Expected Tool | Key Assertions |
|-----------|-------|---------------|----------------|
| 11 | "Run an ESG compliance check" | `compliance_check` | Score, violations with XOM |
| 12 | "Check for fossil fuel exposure" | `compliance_check` | Category filter, XOM flagged |
| 13 | "Are my holdings ethical?" | `compliance_check` | Score + clean/flagged breakdown |
| 14 | "Any weapons companies in portfolio?" | `compliance_check` | Category filter for weapons |
| 15 | "Give me my compliance score" | `compliance_check` | Numeric score 0-100 |

Design doc: `docs/plans/2026-02-24-agent-eval-harness-design.md`

## Notes
- **This tool IS MVP requirement #7** (domain-specific verification check).
- XOM intentionally seeded in US-002 to make compliance demo meaningful.
- ESG dataset is the foundation for the open-source contribution in Phase 4.
- Can be developed in parallel with US-004.
- Agent accesses holdings via same pattern as US-004 (service injection or internal HTTP).
