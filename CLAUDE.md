# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Treasury Aesthetics Treatment Advisor — a Flask web app that wraps the Anthropic API to act as a physician-led skincare/treatment advisor chatbot for [treasuryhealth.ca](https://treasuryhealth.ca). The agent produces structured treatment plans rendered as interactive widgets in the browser and exportable as branded `.docx` files.

## Running the App

```bash
# Install dependencies (Python 3.12)
pip install -r requirements.txt

# Copy and fill in environment variables
cp .env.example .env

# Development (auto-reload)
FLASK_ENV=development python app.py

# Production (as deployed on Heroku)
gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
```

The app defaults to port `5000`. Set `PORT` env var to override.

## Required Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ | Anthropic API key |
| `SECRET_KEY` | ✅ | Flask session secret |
| `GOOGLE_DRIVE_FOLDER_ID` + `GOOGLE_API_KEY` | Optional | Highest-priority knowledge source |
| `GITHUB_KNOWLEDGE_REPO` + `GITHUB_KNOWLEDGE_PATH` + `GITHUB_TOKEN` | Optional | Secondary knowledge source |

## Architecture

### Request Flow

```
Browser → Flask (app.py)
              ↓
         POST /chat → SkincareAgent.chat() (agent.py)
                          ↓
                     Anthropic Messages API
                     (system = SYSTEM_INTRO + knowledge, with prompt caching)
                          ↓
                     response text containing <plan>{JSON}</plan>
              ↓
         POST /export → generate_plan_docx() (export_docx.py)
                            ↓
                        .docx bytes streamed to browser
```

### Key Files

- **`agent.py`** — `SkincareAgent` class. Holds the full `SYSTEM_INTRO` (the hard-coded clinical ruleset) and loads the knowledge base at startup via `knowledge_loader.py`. Applies Anthropic prompt caching (`cache_control: ephemeral`) to the knowledge block so repeated calls don't reprocess it. Model is `claude-sonnet-4-6`.

- **`knowledge_loader.py`** — Three-tier knowledge loading at startup: **Google Drive** (PDFs, `.md`, `.txt`) → **GitHub repo folder** → **local `knowledge/` directory**. All sources concatenate text with `=== Section Title ===` separators.

- **`export_docx.py`** — Generates a branded Word document from the treatment plan JSON dict. Uses `python-docx` with Treasury Aesthetics brand colours (charcoal `#1A1A1A`, gold `#C4954A`).

- **`templates/index.html`** — Single-file frontend (no build step). Parses `<plan>…</plan>` tags from API responses and renders an interactive plan widget (checkboxes, add/remove items). The widget's live state (including user edits) is serialised back to JSON and sent to `/export`.

- **`load_pdf.py`** — CLI utility: extracts text from a PDF → saves to `knowledge/<name>.txt` → optionally `git push`es it.

### Treatment Plan Protocol

The agent always appends a `<plan>` tag containing valid JSON:

```json
{
  "title": "Plan title",
  "sections": [
    {
      "name": "In-Clinic Treatments",
      "items": [{ "name": "Treatment", "detail": "Frequency", "checked": true }]
    }
  ]
}
```

Standard section names: `In-Clinic Treatments`, `Biologics & Add-Ons`, `Morning Routine`, `Evening Routine`, `Post-Procedure Recovery`, `Membership`. `checked: true` = core item, `checked: false` = optional add-on.

## Adding / Updating Knowledge

```bash
# Extract a PDF and add to knowledge (commits + pushes automatically if GITHUB_KNOWLEDGE_REPO is set)
python load_pdf.py path/to/document.pdf

# Local only, no git push
python load_pdf.py path/to/document.pdf --no-push
```

You can also drop `.md` or `.txt` files directly into `knowledge/`. The agent reloads knowledge on every app restart — there is no live reload.

## Deployment

Deployed on Heroku via `Procfile`. Python version is pinned to `3.12` in `runtime.txt`. Single worker is intentional (the Anthropic client is stateless per request; `SkincareAgent` is initialised once at startup and shared).
