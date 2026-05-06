# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AI Job Foundry** — automated job scraping + FIT scoring + auto-apply pipeline for Marcos Alvarado (PM Senior, Guadalajara MX).

Pipeline flow:
1. **GHA scraper** (daily 10am MX / 16:00 UTC, Mon-Fri) → LinkedIn + Computrabajo + Adzuna + OCC
2. **FIT scores** (Gemini Flash → NVIDIA NIM → Ollama fallback) → 0-10 score vs Marcos's profile
3. **Auto-apply** (local PC only, never in GHA) → applies to jobs with FIT ≥ 7

Google Sheet: `https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg`  
Tabs: LinkedIn | Computrabajo | Adzuna | OCC | Registry

## Commands

All commands from `C:\dev\ai-job-foundry`. Use `py` (not `python`). Prefix with `$env:PYTHONUTF8="1"` for scripts that use emojis.

```powershell
# Auto-apply (LOCAL ONLY — never runs in GHA)
$env:PYTHONUTF8="1"; py scripts/apply/run_autoapply.py --dry-run --max 5
$env:PYTHONUTF8="1"; py scripts/apply/run_autoapply.py --dry-run --job-id <JOB_ID>
$env:PYTHONUTF8="1"; py scripts/apply/run_autoapply.py --submit --max 3   # real submission

# FIT scores for all tabs (~45-60 min, uses Gemini/NVIDIA/Ollama)
$env:PYTHONUTF8="1"; py scripts/maintenance/calculate_linkedin_fit_scores.py

# Check sheet coverage (FIT scores, tab counts)
$env:PYTHONUTF8="1"; py check_jobs.py

# Trigger GHA scraper manually
gh workflow run daily_scraper.yml --field mode=live
gh run list --limit 5
```

## Architecture

### Canonical Entry Points

| Module | Path | Role |
|--------|------|------|
| `SheetManager` | `core/sheets/sheet_manager.py` | All Google Sheets I/O. Tab auto-creation, header caching, 400-error handling. Single source of truth. |
| `LinkedInAutoApplyV3` | `core/automation/linkedin_auto_apply.py` | LinkedIn Easy Apply via Playwright. Cookies from `data/linkedin_cookies.json`, auto-login from `.env`. |
| `ExternalApplier` | `core/automation/auto_apply_external.py` | Non-LinkedIn ATS (Workable, Greenhouse, Lever, SmartRecruiters, Workday, Generic). AI form-fill. |
| `CVCustomizer` | `core/automation/cv_customizer.py` | Generates job-specific PDFs for FIT ≥ 8. Base CV used for FIT 7. |
| Scrapers | `core/ingestion/` | `linkedin_search_scraper_v3.py`, `computrabajo_scraper.py`, `adzuna_scraper.py`, `occ_scraper.py` |
| Search queries | `core/ingestion/queries.py` | Central list of all scraper queries (EN + ES). Edit here to change what gets scraped. |
| FIT scorer | `scripts/maintenance/calculate_linkedin_fit_scores.py` | Multi-tab, multi-backend AI with automatic 429 fallback. |
| CI orchestrator | `scripts/ci/run_scraper_ci.py` | GHA entry point — runs all scrapers sequentially with `headless=True`. |

### Auto-Apply Flow (`scripts/apply/run_autoapply.py`)

1. Calls `get_high_fit_jobs()` from `linkedin_auto_apply.py` — reads all 4 source tabs, returns FIT ≥ 7 & Status != Applied
2. Routes by job URL:
   - `linkedin.com` URL → `LinkedInAutoApplyV3` (Easy Apply modal)
   - Any other URL → `ExternalApplier` directly (navigate to ATS)
3. After apply, calls `update_sheet_status(job, status)` — uses `job['_source_tab']` to write to the correct tab

### AI Backend Priority

Both `auto_apply_external.py` and `calculate_linkedin_fit_scores.py` use the same fallback chain:
1. LM Studio / Ollama (`LLM_URL` in `.env`, default `http://127.0.0.1:4000`) — always tried first for local runs
2. Gemini Flash (`GEMINI_API_KEY`) — ~15 rpm free tier
3. NVIDIA NIM (`NVIDIA_API_KEY`) — ~5 rpm free tier
4. Hardcoded generic fallback string

### GHA vs Local split

| Component | GHA (Ubuntu) | Local PC |
|-----------|-------------|----------|
| Scrapers | ✅ Daily cron | Can run manually |
| FIT scores | ✅ After each scrape | Can run manually |
| Auto-apply | ❌ Never | ✅ Only here |
| LinkedIn session | `LINKEDIN_AUTH_JSON` secret | `data/linkedin_cookies.json` |
| Google credentials | `GOOGLE_CREDENTIALS_JSON` + `GOOGLE_TOKEN_JSON` secrets | `data/credentials/` |

GHA uses `requirements_ci.txt` (minimal). Local has full `requirements.txt`.

## Active Bug (2026-05-05)

LinkedIn renamed "Easy Apply" → "LinkedIn Apply". The button selector in `scripts/apply/run_autoapply.py` ~line 248 no longer matches.

```python
# Replace broken selector with:
easy_apply = page.query_selector(
    'button:has-text("Easy Apply"), '
    'button[aria-label*="Easy Apply"], '
    'button[aria-label*="easy apply"], '
    'button.jobs-apply-button, '
    '.jobs-apply-button--top-card'
)

# Also: external "Apply" button is <a> not <button> (~line 280):
apply_btn = page.query_selector(
    'button:has-text("Apply"):not(:has-text("Easy")), '
    'a.jobs-apply-button:not([aria-label*="Easy"]), '
    'a[data-tracking-control-name*="apply"]:not([aria-label*="Easy"])'
)
```

Evidence: `logs/debug_apply.png` — `[FOUND] 'Apply': 0 buttons, 10 links`

## Key Constraints

- `data/credentials/`, `data/linkedin_cookies.json`, `.env` — gitignored, local-only. Never read, modify, or commit these.
- Apply filters: skip if visible salary < 65k MXN / $40k USD; skip pure developer roles; skip video-required forms.
- Max 15 LinkedIn applies/day to avoid account flags.
- `SheetManager.get_all_jobs()` and `_get_headers()` return `[]` safely if a tab doesn't exist yet (OCC tab is auto-created on first GHA run).

## Directory Map

```
core/
  automation/     — apply logic (linkedin_auto_apply.py is canonical V3; older files are legacy)
  ingestion/      — scrapers + queries.py
  sheets/         — SheetManager (single Sheets abstraction)
  enrichment/     — FIT score analysis helpers
  utils/          — oauth_validator.py, linkedin_credentials.py
scripts/
  apply/          — run_autoapply.py (production auto-apply runner)
  ci/             — run_scraper_ci.py (GHA entry point)
  maintenance/    — calculate_linkedin_fit_scores.py, cleanup/dedup tools
  oauth/          — token refresh utilities
.github/workflows/
  daily_scraper.yml — cron Mon-Fri 10am MX (16:00 UTC), timeout 65 min
data/
  cv/             — CV_Marcos_Alvarado_2026.pdf (base) + generated/ (custom PDFs per job)
  credentials/    — GITIGNORED
logs/
  autoapply_YYYYMMDD.log
  scraper_YYYYMMDD_HHMMSS.log
```

Many UPPERCASE `.py` files at root level and in `scripts/tests/` are one-off debug scripts from past sessions — not part of the production pipeline.
