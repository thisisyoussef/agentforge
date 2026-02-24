# How To Create User Stories

This project is built story-by-story. Each implementation task should map to one story in `docs/user-stories/`.

## Goal
Write stories that are executable, testable, and deployable to production without ambiguity.

## Rules
1. One story = one user-visible outcome.
2. Keep scope small enough to finish, deploy, and validate in one cycle.
3. Include explicit acceptance criteria and production checks.
4. Always include edge cases and failure behavior.
5. Always include a deployment plan and rollback path.

## Process
1. Copy `TEMPLATE.md` to a new file: `US-XXX-short-title.md`.
2. Fill metadata first (ID, status, priority, owner).
3. Write the story in user-value format (As a / I want / so that).
4. Define in-scope and out-of-scope boundaries.
5. List preconditions (services, secrets, dependencies).
6. Create a numbered implementation plan.
7. Add measurable acceptance criteria.
8. Add test plan across unit/integration/e2e.
9. Add deployment steps and production validation checks.
10. Add risks, edge cases, and rollback action.

## Quality Checklist
- [ ] Story outcome is clear and user-visible.
- [ ] Scope is constrained and explicit.
- [ ] Acceptance criteria are measurable.
- [ ] Test plan covers happy path + failure paths.
- [ ] Deployment/verification steps are concrete and runnable.
- [ ] Includes exact production URLs/endpoints or placeholders to fill.

## Naming Convention
- Folder: `docs/user-stories/`
- File: `US-XXX-short-title.md`
- Example: `US-001-prod-health-check.md`

## Example Workflow
1. Pick next `todo` story.
2. Implement steps in order.
3. Run tests.
4. Deploy to production.
5. Execute "How To Verify In Prod" checks.
6. Mark story `done` and link commit/PR.
