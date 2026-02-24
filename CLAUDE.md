# CLAUDE.md

Canonical agent instructions for this workspace.
If any instruction in other local instruction files conflicts with this file, this file wins.

## Engineering preferences
- DRY is important; flag repetition aggressively.
- Well-tested code is non-negotiable; prefer more tests over fewer.
- Build code that is engineered enough: avoid both fragile hacks and premature abstraction.
- Err toward handling edge cases thoughtfully.
- Prefer explicit over clever.

## Test-Driven Development (TDD) — mandatory
Every feature and bugfix follows Red → Green → Refactor:
1. **Red**: Write failing tests first. Tests must fail for the right reason before any implementation.
2. **Green**: Write the minimum implementation to make tests pass.
3. **Refactor**: Clean up while keeping tests green.

Rules:
- No implementation code without a failing test that motivates it.
- Each story must include a **TDD Plan** section listing specific failing tests before implementation begins.
- Run the full test suite after each green step. Do not accumulate untested code.
- When fixing bugs, write a regression test that reproduces the bug (red), then fix (green).
- Preparation phase is mandatory: read relevant code and docs *before* writing tests.

Every story must include:
- **Preparation Phase**: audit local code, check external docs, document expected shapes and planned failing tests.
- **TDD Plan**: explicit list of test files, test cases, and the order they will be written.
- **Local Validation**: lint, test, and build commands that must all pass before deployment.

## Build verification — mandatory
Unit tests alone do not prove production readiness. After Green phase:
1. **Production build**: Run `npx nx build api --configuration=production` and verify it completes.
2. **Bundle smoke test**: Verify the compiled `dist/apps/api/main.js` can load without errors: `node -e "require('./dist/apps/api/main.js')"` (may fail on missing DB, but must not fail on missing modules).
3. **External dependency check**: Any npm package that uses native bindings, complex internal module structure (cookie managers, fetch wrappers), or dynamic `require()` calls MUST be marked as a webpack external in `apps/api/webpack.config.js`. Examples: `yahoo-finance2`, any package with `.node` binaries.
4. **Generated package.json audit**: After production build, verify `dist/apps/api/package.json` includes all runtime dependencies that were marked as externals.

This catches the class of bugs where tests pass (because they mock externals) but production fails (because webpack mangled the dependency).

## Review protocol (when reviewing/planning before code changes)
- Explain concrete tradeoffs for each issue/recommendation.
- Provide an opinionated recommendation.
- Ask for user input before assuming a direction.

Before starting a review, ask user to choose one mode:
1. BIG CHANGE: interact section-by-section (Architecture -> Code Quality -> Tests -> Performance), max 4 top issues per section.
2. SMALL CHANGE: one question per review section.

For each issue found:
- Include file and line reference.
- Provide 2-3 options (including do nothing where reasonable).
- For each option: implementation effort, risk, impact on other code, maintenance burden.
- Put recommended option first.
- Ask user whether to proceed with recommended option or choose another.

Do not assume user priorities on timeline or scale. After each section, pause for feedback.

## Workspace model (authoritative)
- This repo (`agentforge`) is the master coordination workspace for docs, stories, deployment runbooks, and tracking.
- **All implementation happens in `./ghostfolio`** — a git submodule pointing to our fork of `https://github.com/ghostfolio/ghostfolio.git`.
- Agent code lives inside the Ghostfolio fork as new NestJS modules (API: `apps/api/src/app/agent/`) and Angular components (client: `apps/client/src/app/`).
- Language: **TypeScript**. Agent framework: **@langchain/langgraph** (JS). Tests: **Jest via Nx** (Layers 1-4), **LangSmith eval SDK** (Layer 5).
- Build by user story from `./docs/user-stories/`, execute steps in order, and report status by Story ID.
- Keep planning/eval docs here; keep feature code/tests/PR work in `./ghostfolio`.
- **Eval harness**: `ghostfolio/apps/api/src/app/agent/evals/` — LangSmith-based production eval suite (20 cases, rubric scoring). See `docs/plans/2026-02-24-agent-eval-harness-design.md`.

## Submodule handling
```bash
git submodule update --init    # First clone: initialize ghostfolio submodule
git submodule update --remote  # Pull latest from fork
```

## Environment setup (Ghostfolio fork)

### Prerequisites
- PostgreSQL running locally (or via Docker)
- Redis running locally (or via Docker)

### First-time setup
```bash
cd ghostfolio
cp .env.example .env           # Copy and edit with your local DB credentials
npm install                    # Install deps + generate Prisma client (postinstall hook)
npm run database:push          # Push schema to local DB
npm run database:seed          # Seed initial data
```

### Database commands
```bash
npm run database:migrate       # Run pending migrations (production)
npm run database:push          # Push schema changes (development)
npm run database:seed          # Seed/re-seed data
npm run database:gui           # Open Prisma Studio (visual DB browser)
npm run database:generate-typings  # Regenerate Prisma client after schema changes
```

## Local development commands (Ghostfolio fork)
```bash
cd ghostfolio
npm run start:server           # Start API dev server (watch mode)
npm run start:client           # Start Angular client (separate terminal)
npm run test:api               # Run API tests (loads .env.example automatically)
npm run test:common            # Run common lib tests
npm test                       # Run ALL tests in parallel
npx nx build api               # Build API
npx nx build client            # Build client
npx nx lint api                # Lint API
npx nx lint client             # Lint client
```

## Gotchas
- Tests require `.env.example` to exist — the test runner loads it via `dotenv-cli`.
- `ghostfolio/` is a **git submodule**, not a regular directory. Commits inside it are tracked separately.
- Prisma client must be regenerated after any schema change (`npm run database:generate-typings`).
- API and client must be started in **separate terminals** — there is no single combined dev command.


## Delivery requirements (every completed change)
- Always commit and push changes when done.
- Always deploy to production before closing the task.
- Follow `./DEPLOYMENT_SETUP.md`.
- Assume user validates every change in production.
- Always include direct prod checks with browser-first verification: exact page URL(s), what to click/view, expected UI/result, and clear success/failure signals.
- Do not provide `curl` or terminal verification commands unless the user explicitly asks for them.

## Definition of Done (required checklist)
A task is only done when all are true:
- [ ] Story scope completed and status updated in `docs/user-stories/`.
- [ ] Relevant tests added/updated and passing locally/CI.
- [ ] Code committed and pushed to remote.
- [ ] Production deployment completed successfully.
- [ ] Production verification executed with explicit evidence:
  - [ ] URL(s) opened in browser
  - [ ] expected page state/output observed
  - [ ] success/failure outcome recorded
- [ ] Rollback path identified for the change.
- [ ] Handoff includes: Story ID, commit SHA, deployed URL(s), verification result.
