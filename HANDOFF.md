# Skincare Backend Agent — Handoff

> Last updated: 2026-07-15

## Patient Plan System (new — 2026-07-15)

Structured, editable, DOB-protected patient plan pages. Replaces the opaque-HTML
publish flow for new plans (legacy `/api/publish-page` + `/<slug>.html` still work).

**Data:** one JSON file per patient at `{volume}/plans/<slug>.json` — patient
(name + DOB), concern, title, overview, technologies (name/why/timeline/optional),
pre_care, post_care, products (brand_name/generic_name/detail/use_generic/optional).
Module: `patient_plans.py` (storage, validation, DOB verification, signed unlock
tokens via itsdangerous, per-slug brute-force throttle: 15 fails/hour).

**Routes:**
- `GET /p/<slug>` — patient page (`templates/plan_view.html`). DOB gate; correct
  DOB → signed 12h token + plan JSON (DOB never echoed back). Each home-care
  product has an "I'll use my own" button that swaps the brand name for its
  generic descriptor (e.g. Epicutis Lipid Serum → "Hydrating lipid recovery
  serum") and persists via `POST /api/plans/<slug>/preferences` (unlock token
  required).
- `GET /staff` — staff editor (`templates/staff.html`), sign in with
  `PUBLISH_TOKEN`. List / edit / delete every field of every plan, including
  reverting a patient's generic-product choice.
- `POST /api/staff/plans/publish` — Bearer `PUBLISH_TOKEN`. Takes a chat
  `<plan>` JSON + patient name/DOB/concern; Claude restructures it into the
  patient-page format (overview, timelines, pre/post care, generic product
  names); deterministic fallback mapping if the AI call fails.
- `GET/PUT/DELETE /api/staff/plans[/<slug>]` — CRUD, Bearer `PUBLISH_TOKEN`.

**Chat UI:** every plan widget now has a gold **Publish** button → modal
(patient name, DOB, concern, slug auto-filled; staff token asked once, then
kept in localStorage) → posts to the publish route and drops the patient +
edit links into the chat.

**Env:** no new vars required. Unlock-token signing uses `SECRET_KEY` if set,
else `PUBLISH_TOKEN`. `data/` is gitignored (patient data never committed);
in production plans live on the Railway volume.



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

## Live consult listener (speech-to-text → notes + plan)

Built and verified live this session. A mic button in the chat UI
(`templates/index.html`) starts the browser's native `SpeechRecognition`
API (continuous + interim results) — audio never leaves the device; only
the resulting transcript *text* is sent to the server, and only once the
consult is stopped. Auto-restarts recognition through natural pauses while
the consult is active (some browsers silently end a recognition session
after a few seconds of silence even with `continuous: true`).

- **Browser support:** Chrome/Edge only (`webkitSpeechRecognition`). The
  mic button disables itself with an explanatory tooltip on unsupported
  browsers (Safari, Firefox) rather than failing silently.
- **`POST /api/process-consult`** — `{transcript}` → `SkincareAgent.process_consult()`,
  which reuses the exact same system prompt (clinical rules + knowledge
  base) as normal chat, with an added instruction to extract session notes
  then build a plan from the transcript using the same `<plan>{json}</plan>`
  tag format the chat UI already renders. No new frontend rendering code —
  the reply is passed straight to the existing `addMessage()`/`buildPlanWidget()`.
- Rejects transcripts under 20 characters (not enough to process).
- **Not yet tested:** real in-clinic conditions — multiple speakers,
  background noise, clinical terminology recognition accuracy. The text
  test above used a clean, single-narrator transcript; live mic accuracy
  in a real consult room is unverified.
