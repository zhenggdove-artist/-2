# Supabase Keepalive Worker

Primary keepalive for the Supabase leaderboard project.

GitHub Actions scheduled workflows are only a backup here. GitHub disables scheduled workflows in public repositories after 60 days without repository activity, which is exactly the failure mode that stopped the previous keepalive.

## What It Does

- Runs on Cloudflare Workers Cron every 6 hours.
- Sends 2 authenticated read requests to `defender_leaderboard` per run.
- Exposes `/health` for manual verification.
- Optionally posts failures to `ALERT_WEBHOOK` if that secret is configured.

## Deploy

From this directory:

```powershell
npx wrangler whoami
npx wrangler deploy --config wrangler.jsonc
```

Cron trigger changes can take up to 15 minutes to propagate.

## Manual Check

After deploy, open the Worker URL or `/health`. A healthy response looks like:

```json
{
  "ok": true,
  "reason": "manual-http",
  "table": "defender_leaderboard"
}
```

If it returns `502`, check whether the Supabase project is paused or whether the project ref/API key changed.

## Optional Alert

Set a webhook URL for Discord, Slack, or another monitor:

```powershell
npx wrangler secret put ALERT_WEBHOOK --config wrangler.jsonc
```

The Worker still runs without this secret; failures are visible in Cloudflare Worker logs.
