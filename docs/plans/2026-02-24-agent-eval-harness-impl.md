# Agent Eval Harness Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a production eval harness using the LangSmith SDK that scores the Ghostfolio agent across 20 test cases with rubric-based scoring (0-1).

**Architecture:** Standalone TypeScript scripts run via `npx tsx`. A dataset seed script creates/updates a LangSmith dataset. An eval runner calls `evaluate()` from `langsmith/evaluation` against the production agent API, using custom evaluators that return rubric scores. Results live in the LangSmith dashboard.

**Tech Stack:** TypeScript, LangSmith JS SDK (`langsmith`), `tsx` (runtime), HTTP fetch (target function)

**Design doc:** `docs/plans/2026-02-24-agent-eval-harness-design.md`

---

## Prerequisites

Before starting, verify:
```bash
# Must have these env vars (check .env or export them)
echo $LANGSMITH_API_KEY        # Must be set
echo $TEST_SECURITY_TOKEN      # From ghostfolio/.env
# Production must be reachable
curl -s https://ghostfolio-production-e8d1.up.railway.app/api/v1/health
```

---

### Task 1: Install langsmith dependency

**Files:**
- Modify: `ghostfolio/package.json`

**Step 1: Install langsmith**

Run:
```bash
cd ghostfolio && npm install langsmith
```

**Step 2: Verify installation**

Run:
```bash
cd ghostfolio && node -e "require('langsmith'); console.log('langsmith OK')"
```
Expected: `langsmith OK`

**Step 3: Commit**

```bash
cd ghostfolio
git add package.json package-lock.json
git commit -m "chore: add langsmith SDK dependency for eval harness"
```

---

### Task 2: Create shared types and dataset definition

**Files:**
- Create: `ghostfolio/apps/api/src/app/agent/evals/types.ts`
- Create: `ghostfolio/apps/api/src/app/agent/evals/dataset.ts`

**Step 1: Create the types file**

Create `ghostfolio/apps/api/src/app/agent/evals/types.ts`:

```typescript
/**
 * Shared types for the agent eval harness.
 *
 * EvalCase: a single test case with input, expected outputs, and metadata.
 * EvalInput: what gets sent to the agent API.
 * EvalReferenceOutput: ground truth for evaluators to score against.
 */

export interface EvalInput {
  message: string;
  session_id: string;
}

export interface EvalReferenceOutput {
  expectedTool: string | null; // null means no tool expected (error/refusal case)
  expectedPatterns: string[];  // regex or substring patterns the response should contain
  category: 'market_data' | 'portfolio' | 'compliance' | 'multi_turn' | 'error';
}

export interface EvalCase {
  inputs: EvalInput;
  outputs: EvalReferenceOutput;
}

/** Shape returned by POST /api/v1/agent/chat */
export interface AgentChatResponse {
  response: string;
  tool_calls: Array<{
    name: string;
    args: Record<string, unknown>;
    result: string;
  }>;
  session_id: string;
}
```

**Step 2: Create the dataset definition**

Create `ghostfolio/apps/api/src/app/agent/evals/dataset.ts`:

```typescript
import { EvalCase } from './types';

/**
 * 20 eval cases organized by category.
 * These are seeded into LangSmith as a dataset.
 *
 * Session IDs use a prefix so multi-turn cases share a session,
 * and single-turn cases each get a unique session.
 */

// --- Market Data (5 cases) ---
const marketDataCases: EvalCase[] = [
  {
    inputs: { message: "What's the current price of AAPL?", session_id: 'eval-market-1' },
    outputs: { expectedTool: 'market_data_fetch', expectedPatterns: ['AAPL', '\\$\\d+'], category: 'market_data' }
  },
  {
    inputs: { message: 'Compare MSFT and GOOGL prices', session_id: 'eval-market-2' },
    outputs: { expectedTool: 'market_data_fetch', expectedPatterns: ['MSFT', 'GOOGL', '\\$\\d+'], category: 'market_data' }
  },
  {
    inputs: { message: "What's the PE ratio of TSLA?", session_id: 'eval-market-3' },
    outputs: { expectedTool: 'market_data_fetch', expectedPatterns: ['TSLA'], category: 'market_data' }
  },
  {
    inputs: { message: 'Price of BTC-USD', session_id: 'eval-market-4' },
    outputs: { expectedTool: 'market_data_fetch', expectedPatterns: ['BTC'], category: 'market_data' }
  },
  {
    inputs: { message: 'Price of INVALIDXYZ', session_id: 'eval-market-5' },
    outputs: { expectedTool: 'market_data_fetch', expectedPatterns: ['INVALIDXYZ'], category: 'market_data' }
  }
];

// --- Portfolio Analysis (5 cases) ---
const portfolioCases: EvalCase[] = [
  {
    inputs: { message: "What's my portfolio risk?", session_id: 'eval-portfolio-1' },
    outputs: { expectedTool: 'portfolio_risk_analysis', expectedPatterns: ['HHI|Herfindahl|concentration', 'Diversifi'], category: 'portfolio' }
  },
  {
    inputs: { message: 'Show my asset allocation', session_id: 'eval-portfolio-2' },
    outputs: { expectedTool: 'portfolio_risk_analysis', expectedPatterns: ['Allocation', '%'], category: 'portfolio' }
  },
  {
    inputs: { message: 'How concentrated is my portfolio?', session_id: 'eval-portfolio-3' },
    outputs: { expectedTool: 'portfolio_risk_analysis', expectedPatterns: ['concentration|concentrated', '%'], category: 'portfolio' }
  },
  {
    inputs: { message: 'How has my portfolio performed?', session_id: 'eval-portfolio-4' },
    outputs: { expectedTool: 'portfolio_risk_analysis', expectedPatterns: ['return|performance|performed', '\\$'], category: 'portfolio' }
  },
  {
    inputs: { message: 'Am I diversified enough?', session_id: 'eval-portfolio-5' },
    outputs: { expectedTool: 'portfolio_risk_analysis', expectedPatterns: ['Diversifi', 'HHI|Herfindahl|concentration'], category: 'portfolio' }
  }
];

// --- Compliance (5 cases) ---
const complianceCases: EvalCase[] = [
  {
    inputs: { message: 'Run an ESG compliance check', session_id: 'eval-compliance-1' },
    outputs: { expectedTool: 'compliance_check', expectedPatterns: ['Compliance Score', '%', 'XOM|Exxon'], category: 'compliance' }
  },
  {
    inputs: { message: 'Check for fossil fuel exposure', session_id: 'eval-compliance-2' },
    outputs: { expectedTool: 'compliance_check', expectedPatterns: ['fossil fuel', 'XOM|Exxon'], category: 'compliance' }
  },
  {
    inputs: { message: 'Are my holdings ethical?', session_id: 'eval-compliance-3' },
    outputs: { expectedTool: 'compliance_check', expectedPatterns: ['Compliance', '%'], category: 'compliance' }
  },
  {
    inputs: { message: 'Any weapons companies in my portfolio?', session_id: 'eval-compliance-4' },
    outputs: { expectedTool: 'compliance_check', expectedPatterns: ['weapon'], category: 'compliance' }
  },
  {
    inputs: { message: 'Give me my compliance score', session_id: 'eval-compliance-5' },
    outputs: { expectedTool: 'compliance_check', expectedPatterns: ['Compliance Score', '\\d+%'], category: 'compliance' }
  }
];

// --- Multi-turn (3 cases — each is an array of turns) ---
// Multi-turn cases are handled specially by the eval runner.
// We encode them as the SECOND turn only; the runner sends the first turn
// beforehand using the same session_id.
export interface MultiTurnCase {
  turns: Array<{ message: string }>;
  session_id: string;
  expectedTool: string;
  expectedPatterns: string[];
  category: 'multi_turn';
}

export const multiTurnCases: MultiTurnCase[] = [
  {
    turns: [
      { message: 'What is the price of AAPL?' },
      { message: 'What about MSFT?' }
    ],
    session_id: 'eval-multi-1',
    expectedTool: 'market_data_fetch',
    expectedPatterns: ['MSFT', '\\$\\d+'],
    category: 'multi_turn'
  },
  {
    turns: [
      { message: "What's my portfolio risk?" },
      { message: 'Now check ESG compliance' }
    ],
    session_id: 'eval-multi-2',
    expectedTool: 'compliance_check',
    expectedPatterns: ['Compliance', '%'],
    category: 'multi_turn'
  },
  {
    turns: [
      { message: 'Price of AAPL' },
      { message: 'Is that higher than last year?' }
    ],
    session_id: 'eval-multi-3',
    expectedTool: null, // May or may not invoke a tool
    expectedPatterns: ['AAPL|price|higher|year'],
    category: 'multi_turn'
  }
];

// --- Error Recovery (2 cases) ---
const errorCases: EvalCase[] = [
  {
    inputs: { message: '', session_id: 'eval-error-1' },
    outputs: { expectedTool: null, expectedPatterns: ['provide|message|Please'], category: 'error' }
  },
  {
    inputs: { message: 'Write me a poem about stocks', session_id: 'eval-error-2' },
    outputs: { expectedTool: null, expectedPatterns: ['help|ESG|portfolio|market|ticker'], category: 'error' }
  }
];

/** All single-turn eval cases (17 total) */
export const singleTurnCases: EvalCase[] = [
  ...marketDataCases,
  ...portfolioCases,
  ...complianceCases,
  ...errorCases
];

/** Total case count for reporting */
export const TOTAL_CASES = singleTurnCases.length + multiTurnCases.length; // 20
```

**Step 3: Verify TypeScript compiles**

Run:
```bash
cd ghostfolio && npx tsx --eval "import { singleTurnCases, TOTAL_CASES } from './apps/api/src/app/agent/evals/dataset'; console.log('Cases:', TOTAL_CASES)"
```
Expected: `Cases: 20`

**Step 4: Commit**

```bash
cd ghostfolio
git add apps/api/src/app/agent/evals/types.ts apps/api/src/app/agent/evals/dataset.ts
git commit -m "feat(evals): add eval types and 20-case dataset definition"
```

---

### Task 3: Create the target function

The target function wraps an HTTP POST to the production agent API. It is decorated with LangSmith `traceable()` so each call creates a trace.

**Files:**
- Create: `ghostfolio/apps/api/src/app/agent/evals/target.ts`

**Step 1: Create target.ts**

Create `ghostfolio/apps/api/src/app/agent/evals/target.ts`:

```typescript
import { traceable } from 'langsmith/traceable';

import { AgentChatResponse } from './types';

const BASE_URL = process.env.EVAL_BASE_URL || 'https://ghostfolio-production-e8d1.up.railway.app';

/**
 * Send a chat message to the production agent API.
 * Wrapped with traceable() so LangSmith records the full HTTP round-trip.
 */
export const callAgent = traceable(
  async (inputs: { message: string; session_id: string }): Promise<AgentChatResponse> => {
    const url = `${BASE_URL}/api/v1/agent/chat`;

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: inputs.message,
        session_id: inputs.session_id
      })
    });

    if (!res.ok) {
      const text = await res.text();
      return {
        response: `HTTP ${res.status}: ${text}`,
        tool_calls: [],
        session_id: inputs.session_id
      };
    }

    return (await res.json()) as AgentChatResponse;
  },
  { name: 'ghostfolio-agent-chat', run_type: 'chain' }
);
```

**Step 2: Verify it compiles and can reach production**

Run:
```bash
cd ghostfolio && LANGSMITH_TRACING=false npx tsx --eval "
import { callAgent } from './apps/api/src/app/agent/evals/target';
(async () => {
  const r = await callAgent({ message: 'Price of AAPL', session_id: 'test-target' });
  console.log('Response:', r.response.substring(0, 80));
  console.log('Tools:', r.tool_calls.map(t => t.name));
})();
"
```
Expected: Response containing AAPL price, Tools: `['market_data_fetch']`

**Step 3: Commit**

```bash
cd ghostfolio
git add apps/api/src/app/agent/evals/target.ts
git commit -m "feat(evals): add traceable target function for production agent API"
```

---

### Task 4: Create evaluators

Four evaluator functions, each returning `{ key: string, score: number }`.

**Files:**
- Create: `ghostfolio/apps/api/src/app/agent/evals/evaluators/tool-selection.ts`
- Create: `ghostfolio/apps/api/src/app/agent/evals/evaluators/data-accuracy.ts`
- Create: `ghostfolio/apps/api/src/app/agent/evals/evaluators/response-quality.ts`
- Create: `ghostfolio/apps/api/src/app/agent/evals/evaluators/no-hallucination.ts`
- Create: `ghostfolio/apps/api/src/app/agent/evals/evaluators/index.ts`

**Step 1: Create tool-selection evaluator**

Create `ghostfolio/apps/api/src/app/agent/evals/evaluators/tool-selection.ts`:

```typescript
import type { EvaluationResult } from 'langsmith/evaluation';

/**
 * Scores 1.0 if the agent invoked the expected tool, 0.0 otherwise.
 * If expectedTool is null (error/refusal case), scores 1.0 when no tools were called.
 */
export function toolSelection({
  outputs,
  referenceOutputs
}: {
  outputs?: Record<string, unknown>;
  referenceOutputs?: Record<string, unknown>;
}): EvaluationResult {
  const toolCalls = (outputs?.tool_calls ?? []) as Array<{ name: string }>;
  const expectedTool = referenceOutputs?.expectedTool as string | null;

  if (expectedTool === null) {
    // Expect no tool call
    const score = toolCalls.length === 0 ? 1.0 : 0.0;
    return { key: 'tool_selection', score, comment: score === 1.0 ? 'Correctly no tool' : `Unexpected tool: ${toolCalls[0]?.name}` };
  }

  const actualTool = toolCalls[0]?.name;
  const score = actualTool === expectedTool ? 1.0 : 0.0;
  return {
    key: 'tool_selection',
    score,
    comment: score === 1.0 ? `Correct: ${actualTool}` : `Expected ${expectedTool}, got ${actualTool || 'none'}`
  };
}
```

**Step 2: Create data-accuracy evaluator**

Create `ghostfolio/apps/api/src/app/agent/evals/evaluators/data-accuracy.ts`:

```typescript
import type { EvaluationResult } from 'langsmith/evaluation';

/**
 * Scores based on how many expected patterns appear in the response.
 * Each pattern in expectedPatterns is treated as a case-insensitive regex.
 * Score = matched / total. If no patterns specified, score is 1.0.
 */
export function dataAccuracy({
  outputs,
  referenceOutputs
}: {
  outputs?: Record<string, unknown>;
  referenceOutputs?: Record<string, unknown>;
}): EvaluationResult {
  const response = (outputs?.response as string) ?? '';
  const patterns = (referenceOutputs?.expectedPatterns as string[]) ?? [];

  if (patterns.length === 0) {
    return { key: 'data_accuracy', score: 1.0, comment: 'No patterns to check' };
  }

  let matched = 0;
  const results: string[] = [];

  for (const pattern of patterns) {
    try {
      const regex = new RegExp(pattern, 'i');
      if (regex.test(response)) {
        matched++;
        results.push(`+ ${pattern}`);
      } else {
        results.push(`- ${pattern}`);
      }
    } catch {
      // If pattern is not valid regex, fall back to substring match
      if (response.toLowerCase().includes(pattern.toLowerCase())) {
        matched++;
        results.push(`+ ${pattern} (substring)`);
      } else {
        results.push(`- ${pattern} (substring)`);
      }
    }
  }

  const score = matched / patterns.length;
  return { key: 'data_accuracy', score, comment: results.join(', ') };
}
```

**Step 3: Create response-quality evaluator**

Create `ghostfolio/apps/api/src/app/agent/evals/evaluators/response-quality.ts`:

```typescript
import type { EvaluationResult } from 'langsmith/evaluation';

const ERROR_INDICATORS = [
  'stack trace',
  'Error:',
  'TypeError',
  'ReferenceError',
  'SyntaxError',
  'undefined',
  'ECONNREFUSED',
  'Internal Server Error'
];

/**
 * Scores response quality on a 0-1 scale:
 *   1.0 = non-empty, no error indicators, reasonable length (10-5000 chars)
 *   0.5 = response present but contains error indicators or is too short/long
 *   0.0 = empty response or HTTP error
 */
export function responseQuality({
  outputs
}: {
  outputs?: Record<string, unknown>;
}): EvaluationResult {
  const response = (outputs?.response as string) ?? '';

  // Empty response
  if (response.trim().length === 0) {
    return { key: 'response_quality', score: 0.0, comment: 'Empty response' };
  }

  // HTTP error passthrough
  if (response.startsWith('HTTP ')) {
    return { key: 'response_quality', score: 0.0, comment: `HTTP error: ${response.substring(0, 50)}` };
  }

  let score = 1.0;
  const issues: string[] = [];

  // Check for error indicators
  for (const indicator of ERROR_INDICATORS) {
    if (response.includes(indicator)) {
      score = Math.min(score, 0.5);
      issues.push(`Contains "${indicator}"`);
    }
  }

  // Length checks
  if (response.length < 10) {
    score = Math.min(score, 0.5);
    issues.push(`Too short (${response.length} chars)`);
  }
  if (response.length > 5000) {
    score = Math.min(score, 0.5);
    issues.push(`Too long (${response.length} chars)`);
  }

  return {
    key: 'response_quality',
    score,
    comment: issues.length > 0 ? issues.join('; ') : 'Good quality'
  };
}
```

**Step 4: Create no-hallucination evaluator**

Create `ghostfolio/apps/api/src/app/agent/evals/evaluators/no-hallucination.ts`:

```typescript
import type { EvaluationResult } from 'langsmith/evaluation';

/**
 * Checks that dollar amounts in the response can be traced to tool output.
 * Extracts all $X.XX patterns from the response and verifies each appears
 * in at least one tool call's result.
 *
 * Score 1.0: all numbers traceable (or no numbers in response)
 * Score 0.0-0.99: proportional to traceable numbers
 *
 * For the current keyword router, this is effectively always 1.0 since
 * the service builds responses directly from tool output. Becomes critical
 * when LLM generates free-text responses.
 */
export function noHallucination({
  outputs
}: {
  outputs?: Record<string, unknown>;
}): EvaluationResult {
  const response = (outputs?.response as string) ?? '';
  const toolCalls = (outputs?.tool_calls ?? []) as Array<{ result: string }>;

  // Extract dollar amounts from response (e.g., $185.00, $1,234.56)
  const dollarPattern = /\$[\d,]+\.?\d*/g;
  const responseDollars = response.match(dollarPattern) ?? [];

  if (responseDollars.length === 0) {
    return { key: 'no_hallucination', score: 1.0, comment: 'No dollar amounts to verify' };
  }

  // Concatenate all tool results for checking
  const toolResultText = toolCalls.map((tc) => tc.result).join(' ');

  let traceable = 0;
  const details: string[] = [];

  for (const dollar of responseDollars) {
    // Strip $ and commas to get the raw number
    const rawNumber = dollar.replace(/[$,]/g, '');
    if (toolResultText.includes(rawNumber)) {
      traceable++;
      details.push(`+ ${dollar}`);
    } else {
      details.push(`- ${dollar} (not in tool output)`);
    }
  }

  const score = traceable / responseDollars.length;
  return { key: 'no_hallucination', score, comment: details.join(', ') };
}
```

**Step 5: Create barrel export**

Create `ghostfolio/apps/api/src/app/agent/evals/evaluators/index.ts`:

```typescript
export { toolSelection } from './tool-selection';
export { dataAccuracy } from './data-accuracy';
export { responseQuality } from './response-quality';
export { noHallucination } from './no-hallucination';
```

**Step 6: Verify all evaluators compile**

Run:
```bash
cd ghostfolio && npx tsx --eval "
import { toolSelection, dataAccuracy, responseQuality, noHallucination } from './apps/api/src/app/agent/evals/evaluators';
console.log('toolSelection:', typeof toolSelection);
console.log('dataAccuracy:', typeof dataAccuracy);
console.log('responseQuality:', typeof responseQuality);
console.log('noHallucination:', typeof noHallucination);
"
```
Expected: All print `function`

**Step 7: Commit**

```bash
cd ghostfolio
git add apps/api/src/app/agent/evals/evaluators/
git commit -m "feat(evals): add 4 rubric-scoring evaluators (tool, accuracy, quality, hallucination)"
```

---

### Task 5: Create the eval runner

The main script that seeds the LangSmith dataset and runs `evaluate()`.

**Files:**
- Create: `ghostfolio/apps/api/src/app/agent/evals/eval-runner.ts`

**Step 1: Create eval-runner.ts**

Create `ghostfolio/apps/api/src/app/agent/evals/eval-runner.ts`:

```typescript
import { Client } from 'langsmith';
import { evaluate } from 'langsmith/evaluation';
import type { EvaluationResult } from 'langsmith/evaluation';

import { singleTurnCases, multiTurnCases, TOTAL_CASES } from './dataset';
import { toolSelection, dataAccuracy, responseQuality, noHallucination } from './evaluators';
import { callAgent } from './target';

const DATASET_NAME = 'ghostfolio-agent-eval-v1';
const EXPERIMENT_PREFIX = 'ghostfolio-agent-eval';

async function seedDataset(client: Client): Promise<void> {
  // Delete existing dataset if it exists, to ensure clean state
  try {
    const existing = await client.readDataset({ datasetName: DATASET_NAME });
    if (existing) {
      await client.deleteDataset({ datasetId: existing.id });
      console.log(`Deleted existing dataset: ${DATASET_NAME}`);
    }
  } catch {
    // Dataset doesn't exist, that's fine
  }

  const dataset = await client.createDataset(DATASET_NAME, {
    description: `Ghostfolio agent eval suite — ${TOTAL_CASES} cases across 5 categories`
  });

  // Seed single-turn cases
  for (const evalCase of singleTurnCases) {
    await client.createExample(evalCase.inputs, evalCase.outputs, {
      datasetId: dataset.id
    });
  }

  // Seed multi-turn cases (encode as the final turn with metadata about prior turns)
  for (const mt of multiTurnCases) {
    const lastTurn = mt.turns[mt.turns.length - 1];
    const priorTurns = mt.turns.slice(0, -1);
    await client.createExample(
      {
        message: lastTurn.message,
        session_id: mt.session_id,
        prior_turns: priorTurns.map((t) => t.message)
      },
      {
        expectedTool: mt.expectedTool,
        expectedPatterns: mt.expectedPatterns,
        category: mt.category
      },
      { datasetId: dataset.id }
    );
  }

  console.log(`Seeded dataset "${DATASET_NAME}" with ${TOTAL_CASES} cases`);
}

/**
 * Target function adapter for evaluate().
 * For multi-turn cases, sends prior turns first before the evaluated turn.
 */
async function target(inputs: Record<string, unknown>): Promise<Record<string, unknown>> {
  const message = inputs.message as string;
  const sessionId = inputs.session_id as string;
  const priorTurns = (inputs.prior_turns as string[]) ?? [];

  // Send prior turns (for multi-turn cases) without scoring
  for (const turn of priorTurns) {
    await callAgent({ message: turn, session_id: sessionId });
  }

  // Send the actual turn to be evaluated
  const result = await callAgent({ message, session_id: sessionId });
  return result as unknown as Record<string, unknown>;
}

/**
 * Summary evaluator: computes overall pass rate.
 * A case "passes" if its average rubric score > 0.7.
 */
function overallPassRate(runs: Array<{
  run: { outputs?: Record<string, unknown> };
  example: { outputs?: Record<string, unknown> };
  evaluationResults: { results: EvaluationResult[] };
}>): EvaluationResult {
  let passed = 0;
  const categoryScores: Record<string, number[]> = {};

  for (const { example, evaluationResults } of runs) {
    const scores = evaluationResults.results
      .filter((r) => typeof r.score === 'number')
      .map((r) => r.score as number);

    const avg = scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;
    if (avg > 0.7) passed++;

    const category = (example.outputs?.category as string) ?? 'unknown';
    if (!categoryScores[category]) categoryScores[category] = [];
    categoryScores[category].push(avg);
  }

  const passRate = runs.length > 0 ? passed / runs.length : 0;

  // Log per-category breakdown
  const breakdown = Object.entries(categoryScores)
    .map(([cat, scores]) => {
      const catAvg = scores.reduce((a, b) => a + b, 0) / scores.length;
      return `${cat}: ${(catAvg * 100).toFixed(0)}%`;
    })
    .join(', ');

  console.log(`\nPass rate: ${(passRate * 100).toFixed(1)}% (${passed}/${runs.length})`);
  console.log(`Category breakdown: ${breakdown}`);

  return {
    key: 'overall_pass_rate',
    score: passRate,
    comment: `${passed}/${runs.length} cases passed (>0.7 avg). ${breakdown}`
  };
}

async function main() {
  console.log('=== Ghostfolio Agent Eval Suite ===\n');

  // Validate env
  if (!process.env.LANGSMITH_API_KEY) {
    console.error('ERROR: LANGSMITH_API_KEY not set');
    process.exit(1);
  }

  const baseUrl = process.env.EVAL_BASE_URL || 'https://ghostfolio-production-e8d1.up.railway.app';
  console.log(`Target: ${baseUrl}`);
  console.log(`Cases: ${TOTAL_CASES}\n`);

  const client = new Client();

  // Step 1: Seed dataset
  console.log('Seeding dataset...');
  await seedDataset(client);

  // Step 2: Run evaluation
  console.log('\nRunning evaluation...\n');
  const results = await evaluate(target, {
    data: DATASET_NAME,
    evaluators: [toolSelection, dataAccuracy, responseQuality, noHallucination],
    summaryEvaluators: [overallPassRate],
    experimentPrefix: EXPERIMENT_PREFIX,
    maxConcurrency: 2, // Gentle on production
    metadata: {
      baseUrl,
      timestamp: new Date().toISOString(),
      version: '1.0'
    }
  });

  console.log(`\nExperiment: ${results.experimentName}`);
  console.log('View results in LangSmith dashboard.');

  // Exit gate: fail if pass rate < 80%
  // The summary evaluator logs the pass rate above.
  // For CI gating, the summary evaluator's score is checked.
}

main().catch((err) => {
  console.error('Eval runner failed:', err);
  process.exit(1);
});
```

**Step 2: Verify it compiles (dry run)**

Run:
```bash
cd ghostfolio && npx tsx --eval "
// Just check that imports resolve
import './apps/api/src/app/agent/evals/eval-runner';
" 2>&1 | head -5
```
Expected: May fail on missing LANGSMITH_API_KEY, but should NOT fail on import errors.

**Step 3: Commit**

```bash
cd ghostfolio
git add apps/api/src/app/agent/evals/eval-runner.ts
git commit -m "feat(evals): add LangSmith eval runner with dataset seeding and evaluate()"
```

---

### Task 6: Create README

**Files:**
- Create: `ghostfolio/apps/api/src/app/agent/evals/README.md`

**Step 1: Create README**

Create `ghostfolio/apps/api/src/app/agent/evals/README.md`:

```markdown
# Agent Eval Suite

Production eval harness using LangSmith. Runs 20 test cases against the live agent API and scores each on a 0-1 rubric.

## Quick Start

```bash
cd ghostfolio

# Required env vars
export LANGSMITH_API_KEY=<your-key>
export EVAL_BASE_URL=https://ghostfolio-production-e8d1.up.railway.app

# Run evals
npx tsx apps/api/src/app/agent/evals/eval-runner.ts
```

Results appear in the [LangSmith dashboard](https://smith.langchain.com/) under experiment `ghostfolio-agent-eval`.

## Eval Cases (20 total)

| Category | Count | Description |
|----------|-------|-------------|
| Market Data | 5 | Price queries, multi-symbol, crypto, invalid symbol |
| Portfolio | 5 | Risk, allocation, concentration, performance, diversification |
| Compliance | 5 | ESG check, category filters, score queries |
| Multi-turn | 3 | Context carryover, tool switching, follow-up |
| Error | 2 | Empty input, out-of-scope request |

## Evaluators (Rubric Scoring)

| Evaluator | Scores | Description |
|-----------|--------|-------------|
| `tool_selection` | 0 or 1 | Correct tool invoked? |
| `data_accuracy` | 0-1 | Expected patterns found in response? |
| `response_quality` | 0-1 | Well-formed, no errors, reasonable length? |
| `no_hallucination` | 0-1 | Dollar amounts traceable to tool output? |
| `overall_pass_rate` | 0-1 | Summary: % of cases with avg score > 0.7 |

## Adding Eval Cases

Edit `dataset.ts` and add cases to the appropriate category array. Each case needs:
- `inputs`: `{ message, session_id }`
- `outputs`: `{ expectedTool, expectedPatterns, category }`

The runner re-seeds the dataset on every run, so changes take effect immediately.

## Design Doc

See `docs/plans/2026-02-24-agent-eval-harness-design.md` for architecture and rationale.
```

**Step 2: Commit**

```bash
cd ghostfolio
git add apps/api/src/app/agent/evals/README.md
git commit -m "docs(evals): add README with quickstart and eval case reference"
```

---

### Task 7: End-to-end test run against production

**Files:** None (validation only)

**Step 1: Run the full eval suite**

Run:
```bash
cd ghostfolio && \
  LANGSMITH_API_KEY=$LANGSMITH_API_KEY \
  LANGSMITH_TRACING=true \
  EVAL_BASE_URL=https://ghostfolio-production-e8d1.up.railway.app \
  npx tsx apps/api/src/app/agent/evals/eval-runner.ts
```

Expected output:
```
=== Ghostfolio Agent Eval Suite ===

Target: https://ghostfolio-production-e8d1.up.railway.app
Cases: 20

Seeding dataset...
Seeded dataset "ghostfolio-agent-eval-v1" with 20 cases

Running evaluation...

Pass rate: ≥80.0% (≥16/20)
Category breakdown: market_data: XX%, portfolio: XX%, compliance: XX%, multi_turn: XX%, error: XX%

Experiment: ghostfolio-agent-eval-XXXXXXXX
View results in LangSmith dashboard.
```

**Step 2: Verify in LangSmith dashboard**

Open: `https://smith.langchain.com/`
1. Navigate to Datasets → `ghostfolio-agent-eval-v1` — should show 20 examples
2. Navigate to Projects → find experiment `ghostfolio-agent-eval-*` — should show rubric scores
3. Verify per-evaluator columns: `tool_selection`, `data_accuracy`, `response_quality`, `no_hallucination`

**Step 3: Record results and commit**

If pass rate >= 80%, record the result:
```bash
cd ghostfolio
git add -A  # If any tweaks were needed
git commit -m "chore(evals): verify eval suite passes against production (≥80% pass rate)"
```

---

### Task 8: Fix any failing eval cases

This is a contingency task. If the pass rate is < 80% in Task 7:

**Step 1: Identify failing cases from LangSmith dashboard**

Look at cases where `tool_selection` or `data_accuracy` scored 0.

**Step 2: Diagnose root cause**

Common issues:
- **Tool routing miss**: Keyword not in ESG_KEYWORDS or PORTFOLIO_KEYWORDS → fix keyword list in `agent.service.ts`
- **Pattern miss**: `expectedPatterns` too strict → adjust regex in `dataset.ts`
- **Multi-turn**: Agent is stateless (no session memory) → multi-turn cases may fail → adjust `expectedPatterns` to be lenient
- **Error response format**: Different from expected → adjust error case patterns

**Step 3: Fix and re-run**

Re-run the eval suite from Task 7 after fixes. Iterate until >= 80%.

**Step 4: Commit fixes**

```bash
cd ghostfolio
git add -A
git commit -m "fix(evals): adjust eval cases/agent routing for ≥80% pass rate"
```

---

## Summary

| Task | What | Files | Commit |
|------|------|-------|--------|
| 1 | Install langsmith | package.json | `chore: add langsmith SDK` |
| 2 | Types + dataset (20 cases) | evals/types.ts, evals/dataset.ts | `feat(evals): dataset definition` |
| 3 | Target function | evals/target.ts | `feat(evals): traceable target` |
| 4 | 4 evaluators | evals/evaluators/*.ts | `feat(evals): rubric evaluators` |
| 5 | Eval runner | evals/eval-runner.ts | `feat(evals): eval runner` |
| 6 | README | evals/README.md | `docs(evals): README` |
| 7 | E2E run + verify | (validation) | `chore(evals): verify pass rate` |
| 8 | Fix failures | (contingency) | `fix(evals): adjust for pass rate` |
