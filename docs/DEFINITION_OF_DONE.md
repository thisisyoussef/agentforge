# Definition of Done Checklist

Use this checklist for every story/change. All items must be complete.

## Core completion
- [ ] Story scope completed.
- [ ] Story status updated in `docs/user-stories/`.
- [ ] Commit SHA and PR/reference recorded in the story.

## Quality
- [ ] Unit/integration/e2e tests added or updated as required.
- [ ] Relevant tests pass locally.
- [ ] CI checks are green (or documented exception approved by user).

## Deployment
- [ ] Change deployed to production successfully.
- [ ] Rollback path identified and documented.

## Production verification (required)
- [ ] Production URL(s) listed in handoff.
- [ ] Endpoint(s)/commands listed in handoff.
- [ ] Expected output documented.
- [ ] Actual output observed and reported.
- [ ] Success/failure criteria explicitly stated.

## Handoff (required)
- [ ] Include Story ID.
- [ ] Include commit SHA.
- [ ] Include deployed URL(s).
- [ ] Include verification commands and results.
- [ ] Include next recommended step (if applicable).
