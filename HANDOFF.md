# Skincare Backend Agent — Handoff

> Last updated: 2026-06-23

## What this is

A Python/Flask staff-facing chat agent for building patient treatment plans
("Skincare backend agent - v2" on Railway). Separate codebase/stack from
`drlatsky-aesthetics/treasury-agent` (the patient-facing Next.js chatbot),
but part of the same overall clinic system — see that repo's
`currentstate.md` for the full ecosystem picture.

## Deployment

- **Platform:** Railway, project "Skincare backend agent - v2", service `web`
- **Public URL:** `https://plans.treasuryaesthetics.ca` (custom domain) /
  `https://web-production-c2fb3.up.railway.app` (Railway-provided fallback —
  same app, same data, both work)
- **Run:** `gunicorn app:app` via `Procfile`
- **Deploy:** `railway up` from this directory deploys the current local
  tree directly (used this session); unclear whether GitHub push also
  triggers an auto-deploy — check Railway dashboard's service settings.
- **Git:** the default/HEAD branch on `origin` is **`claude/skincare-agent-builder-DAd8Q`**,
  not `main` — there is no `main` branch on this repo. Push there. (Also has
  two other `claude/*` branches from prior sessions — `claude/ai-treatment-page-integration-4U0hp`
  and `claude/determined-knuth-ScgSI` — not investigated this session.)

## Railway access

Tokens are in `railway_token.txt` (gitignored, **never commit this file**):
- **Line 1:** project-scoped token. Works for read-only commands (`status`,
  `variables`, `logs`, `up`). Use as `RAILWAY_TOKEN=<value>`.
- **Line 2:** account-level token. Required for `link`, `volume add`, and
  anything else that manages resources rather than just reading/deploying.
  Use as `RAILWAY_API_TOKEN=<value>` (different env var name — the CLI
  treats `RAILWAY_TOKEN` and `RAILWAY_API_TOKEN` differently).

If running on Windows Git Bash, leading `/` in CLI args (e.g.
`--mount-path /data`) gets MSYS-mangled into a Windows path — prefix the
command with `MSYS_NO_PATHCONV=1` to avoid this.

## What changed this session: patient page hosting

This app now owns `plans.treasuryaesthetics.ca` and serves/stores patient
treatment-plan pages directly, replacing an old setup where a separate
generator tool (`drlatsky-aesthetics/treasury-patients` repo) published
pages to GitHub Pages.

- **Railway Volume** `web-volume` (5GB) mounted at `/data` — persists across
  redeploys. Pages live at `/data/pages/<slug>.html`.
- **`POST /api/publish-page`** — body `{slug, html}`, header
  `Authorization: Bearer <PUBLISH_TOKEN>`. Writes `/data/pages/<slug>.html`.
  Slug is validated against `^[a-z0-9][a-z0-9-]{0,79}$` (lowercase
  alphanumeric + hyphens only) to prevent path traversal — reject anything
  else rather than sanitizing it.
- **`GET /<slug>.html`** — serves a previously published page from the
  volume. 404s if the slug doesn't match the same pattern or the file
  doesn't exist.
- **`PUBLISH_TOKEN`** env var on Railway — shared secret the generator tool
  authenticates with. Rotate via `railway variables --set PUBLISH_TOKEN=...`
  if it's ever exposed.
- The generator tool (`treasury-patients/index.html`) was updated to POST
  here instead of committing to GitHub. Its settings panel now asks for
  "Agent URL" + "Publish Token" (saved to the browser's localStorage) instead
  of a GitHub user/repo/PAT/domain.

### DNS

Railway's side was already configured (valid TLS cert since May) — only the
DNS record was missing. **Still needs this CNAME added at the registrar**
(GoDaddy, per the `treasuryaesthetics.ca` zone):

| Type | Name | Value |
|---|---|---|
| CNAME | `plans` | `o5pvawqd.up.railway.app` |

Check `railway domain status plans.treasuryaesthetics.ca --json` if this
needs re-verifying — it'll show `dnsRecords[].currentValue` (empty = not
propagated yet) vs `requiredValue`.

## Known issues / gaps

- `GOOGLE_API_KEY` env var is a placeholder (`your_google_api_key_here`),
  so the app's own attempt to read `GOOGLE_DRIVE_FOLDER_ID` (same Drive
  folder as treasury-agent's Drive Sync) fails with a 400 on every startup
  and falls back to reading `knowledge/*.md` from this repo's own GitHub
  contents instead. Harmless (the fallback works) but means this agent
  doesn't actually see what's dropped in the shared Drive folder.
- No persistent volume existed before this session — any patient pages
  "published" before today via the old GitHub Pages flow live in the
  `treasury-patients` repo, not here.

## Pending feature request (not yet built)

Live speech-to-text during in-person consults — listen in on the
conversation, transcribe it, and feed the resulting transcript to this
agent so it can process the session automatically (build a plan, generate
notes, etc.) without a staff member typing anything. Needs scoping:
audio capture method (browser mic? dedicated recording device?), where
transcription happens (client-side Web Speech API vs. a server-side STT
service), how/when the agent gets triggered (real-time streaming vs.
post-call batch), and what "processed" should produce (a docx, a published
patient page, structured notes, all three?).
