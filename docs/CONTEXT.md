# Live Context Snapshot

Last updated: 2026-02-24

## Repo roles
- Coordination workspace: `https://github.com/thisisyoussef/agentforge`
- Product fork (implementation): `https://github.com/thisisyoussef/ghostfolio`
- Upstream source: `https://github.com/ghostfolio/ghostfolio.git`

## Local paths
- Workspace root: `/Users/youss/Development/gauntlet/agentforge`
- Product code path: `/Users/youss/Development/gauntlet/agentforge/ghostfolio`

## Railway (agentforge project)
- Project name: `agentforge`
- Project id: `a6794fe3-0aa3-4911-bf6b-8ccd995a60f7`
- Backend URL: `https://backend-production-61f8.up.railway.app`
- Frontend URL: `https://frontend-production-a5e0.up.railway.app`
- Backend health endpoint: `https://backend-production-61f8.up.railway.app/health`

## Current workflow
- Plan and track in `docs/user-stories/`.
- Implement feature code in `ghostfolio/` on story-specific branches.
- Deploy and verify in prod for every completed change.

## Standard prod verification commands
```bash
curl -i https://backend-production-61f8.up.railway.app/health
curl -i https://frontend-production-a5e0.up.railway.app/
```

## Open decisions (update as needed)
- Confirm next active story ID.
- Confirm first production feature scope in `ghostfolio`.
