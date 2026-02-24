# CLAUDE.md

Canonical agent instructions for this workspace.
If any instruction in other local instruction files conflicts with this file, this file wins.

## Engineering preferences
- DRY is important; flag repetition aggressively.
- Well-tested code is non-negotiable; prefer more tests over fewer.
- Build code that is engineered enough: avoid both fragile hacks and premature abstraction.
- Err toward handling edge cases thoughtfully.
- Prefer explicit over clever.

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
- Product implementation happens in `./ghostfolio` (fork of `https://github.com/ghostfolio/ghostfolio.git`).
- Build by user story from `./docs/user-stories/`, execute steps in order, and report status by Story ID.
- Keep planning/eval docs here; keep feature code/tests/PR work in `./ghostfolio`.

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
