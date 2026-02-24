# Deployment Setup — Railway + Ghostfolio Fork

## Architecture

All code lives inside the Ghostfolio fork (`./ghostfolio`). One Railway project, three services:
- **Postgres** — managed database
- **Redis** — managed cache
- **ghostfolio** — NestJS API + Angular client (single Dockerfile)

## Railway Project

- **Project name**: `faithful-youthfulness`
- **Project ID**: `ad54fa78-44fe-4b35-bd5b-f3fc8e81e276`
- **Environment**: `production` (`8e84fd91-90f8-4625-9967-f3c3d1a82dea`)
- **Ghostfolio service ID**: `337535e9-3530-4250-aba2-4f724df0405c`
- **Production URL**: `https://ghostfolio-production-e8d1.up.railway.app`

## Required Environment Variables (ghostfolio service)

| Variable | Source | Description |
|----------|--------|-------------|
| `DATABASE_URL` | Postgres internal URL | `postgresql://..@postgres.railway.internal:5432/railway` |
| `REDIS_HOST` | Redis internal domain | `redis.railway.internal` |
| `REDIS_PORT` | Redis port | `6379` |
| `REDIS_PASSWORD` | Redis auto-generated | From Redis service variables |
| `ACCESS_TOKEN_SALT` | Random hex string | `openssl rand -hex 32` |
| `JWT_SECRET_KEY` | Random hex string | `openssl rand -hex 32` |
| `PORT` | Fixed | `3333` |

## Deployment Commands

```bash
# From the ghostfolio directory (not agentforge root)
cd ghostfolio

# Link CLI to project (first time or after re-link)
railway link --project faithful-youthfulness
railway service ghostfolio

# Deploy
railway up --detach

# Check logs
railway logs 2>&1 &; LPID=$!; sleep 10; kill $LPID 2>/dev/null; wait $LPID 2>/dev/null

# Check variables
railway variables
```

## Build Process

The Dockerfile handles everything:
1. **Builder stage**: `npm install` → `npm run build:production` (builds API + client)
2. **Dist stage**: copies `dist/apps/api/`, runs `npm install` on generated package.json
3. **Runtime stage**: `node:22-slim`, runs migrations + seed + `node main`

## Webpack Externals

Packages with complex internals must be marked as externals in `apps/api/webpack.config.js`:
- `yahoo-finance2` — cookie/fetch handlers break when bundled

## Smoke Test

After deployment:
1. Open `https://ghostfolio-production-e8d1.up.railway.app` → Ghostfolio landing page
2. Navigate to `/en/agent` → Agent chat UI
3. Type "What is the price of AAPL?" → Real price data returned

## Rollback

```bash
# List deployments
railway logs --deployment <deployment-id>

# Railway dashboard → service → deployments → click previous → redeploy
```
