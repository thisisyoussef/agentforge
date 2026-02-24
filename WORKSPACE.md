# Master Workspace Layout

This repository is the master coordination workspace.

## Folder roles
- `ghostfolio/`: product code repository (your fork, with upstream set to `ghostfolio/ghostfolio`)
- `docs/user-stories/`: source of truth for build order and acceptance
- `DEPLOYMENT_SETUP.md`: deployment runbook (Railway)
- `agents.md`: canonical agent operating instructions
- `CLAUDE.md`, `cloud.md`: pointer files to canonical instructions
- `docs/CONTEXT.md`: live workspace/deployment context snapshot
- `docs/DEFINITION_OF_DONE.md`: completion checklist for every change

## Build flow (required)
1. Pick next story in `docs/user-stories/`.
2. Implement code in `ghostfolio/` on a story-specific branch.
3. Run tests.
4. Deploy to production.
5. Validate with explicit prod checks.
6. Update story status with commit/PR/prod URLs.

## Repo boundaries
- Keep planning/eval/process docs in this master repo.
- Keep feature code, tests, and open-source PR work in `ghostfolio/`.
- Avoid duplicating full docs into `ghostfolio/`; if needed, add a single pointer file.
