# US-XXX: Title

## Status
- State: `todo | in-progress | blocked | done`
- Owner:
- Depends on:
- Related PR/Commit:
- Target environment: `prod`

## Persona
**<Name, the Role>** wants <goal/motivation>.

## User Story
> As <persona>, I want <capability> so that <outcome/business value>.

## Goal
One-paragraph summary of what this story delivers and why it matters.

## Scope
In scope:
1.
2.
3.

Out of scope:
1.
2.

## Pre-Implementation Audit
Local sources to read before writing any code:
1. `<file path>` — <why>
2. `<file path>` — <why>

## Preparation Phase (Mandatory)
1. Read local code and API contracts listed in Pre-Implementation Audit.
2. Web-check relevant docs before coding:
   - <doc URL or topic>
   - <doc URL or topic>
3. Write Preparation Notes with:
   - Expected API response shapes / data contracts
   - Error handling decisions
   - Planned failing tests (list them here before implementation)

### Preparation Notes
_(Fill during execution — document what you learned before writing tests.)_

Local docs/code reviewed:
1.
2.

Expected data shapes:
1.
2.

Error-handling decisions:
1.
2.

Planned failing tests:
1.
2.
3.

## UX Script
Happy path:
1. User does X.
2. System responds with Y.
3. User sees Z.

Error path:
1. Service fails or returns bad data.
2. User sees graceful error message.
3. User can retry without refreshing.

## Preconditions
- [ ] Required services/accounts exist
- [ ] Required secrets are configured
- [ ] Dependencies are deployed and healthy

## TDD Plan
Write tests first. Red → Green → Refactor.

### Test files to create/modify
1. `<test file path>`
   - Test: <description> — expects <behavior>
   - Test: <description> — expects <behavior>
2. `<test file path>`
   - Test: <description> — expects <behavior>

### Red → Green → Refactor sequence
1. Write failing tests from list above.
2. Run tests — confirm all new tests fail (red).
3. Implement minimum code to pass each test (green).
4. Refactor while keeping tests green.

## Step-by-step Implementation Plan
1.
2.
3.

## Implementation Details
_(Fill during execution.)_

Implemented files:
1.
2.

Key interfaces/schemas:
```
(paste relevant type definitions here during implementation)
```

## Acceptance Criteria
- [ ] AC1:
- [ ] AC2:
- [ ] AC3:

## Local Validation
Run these commands — all must pass before deployment:
```bash
# Lint
<lint command>

# Tests (specific to this story)
<test command for story-specific tests>

# Full test suite
<full test command>

# Production build
npx nx run api:build:production

# Bundle smoke test (verifies all externals resolve at runtime)
# May fail on DB connection — that's OK. Must NOT fail on missing modules.
node -e "require('./dist/apps/api/main.js')" 2>&1 | head -5

# Generated package.json audit (verify all webpack externals are listed)
cat dist/apps/api/package.json | grep -E "<list external package names>"
```

### Build verification checklist
- [ ] Production build completes (with or without pre-existing TS errors)
- [ ] All webpack externals appear in `dist/apps/api/package.json`
- [ ] Bundle smoke test does not fail on missing modules
- [ ] Any new npm package with native bindings or complex internals is added to webpack externals

## Deployment Handoff (Mandatory)
1. Commit implementation and docs on the working branch.
2. Push the branch to `origin`.
3. Deploy to production (Railway auto-deploy from `main`).
4. Record deployed URLs and commit SHA in Checkpoint Result.
5. If deployment is blocked, document blocker and owner in Checkpoint Result.

## How To Verify In Prod (Required)
- Production URL(s):
- Endpoint(s) to call:
- Expected results:
- Failure signals:
- Rollback action:

## User Checkpoint Test
1. Open <URL> and verify <expected state>.
2. Perform <action> and confirm <result>.
3. Trigger <error condition> and confirm <graceful handling>.

## Checkpoint Result
_(Fill after deployment.)_
- Commit SHA:
- Production URL(s):
- User Validation: `passed | failed | blocked`
- Notes:

## Observability & Monitoring
- Logs to check:
- Traces/metrics to check:
- Alert thresholds:

## Risks & Edge Cases
- Risk 1:
- Risk 2:
- Edge case 1:
- Edge case 2:

## Notes
-
