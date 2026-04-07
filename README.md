# AI Job Foundry

> Automated job hunting pipeline — from email to application, powered by local AI.

Gmail → Google Sheets → FIT Score → LinkedIn Easy Apply. No cloud API costs. No resume leaks.

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://python.org)
[![LM Studio](https://img.shields.io/badge/LM_Studio-Qwen_2.5_14B-FF6B35)](https://lmstudio.ai)
[![Playwright](https://img.shields.io/badge/Playwright-Automation-45ba4b)](https://playwright.dev)

---

## Pipeline

```
┌─────────┐   ┌──────────────┐   ┌───────────┐   ┌──────────────┐
│  Gmail  │──▶│ Google Sheets│──▶│ FIT Score │──▶│  Easy Apply  │
│Ingestion│   │  271+ jobs   │   │  (0-10)   │   │ + Cover CL   │
└─────────┘   └──────────────┘   └───────────┘   └──────────────┘
                     │                                    │
             ┌───────▼────────┐                ┌──────────▼──────┐
             │ Dedup + Clean  │                │Telegram Notifier│
             └────────────────┘                └─────────────────┘
```

---

## Features

- [x] Gmail ingestion — parses LinkedIn job alert emails, extracts valid job URLs
- [x] Smart URL normalization — canonical `linkedin.com/jobs/view/{ID}`, filters junk links
- [x] FIT scoring — local LLM rates each job 0-10 against your profile
- [x] Deduplication — removes duplicates and expired listings automatically
- [x] Auto-apply — LinkedIn Easy Apply via Playwright with AI cover letters
- [x] Cover letter generation — tailored per-job CLs using Qwen 2.5 14B locally
- [x] Telegram notifications — morning summary, daily stats, apply confirmations
- [x] Chalan memory — AI learns from past applications across sessions
- [x] US-only filter — auto-detects and skips US-only postings for MX/LATAM applicants
- [x] Windows Task Scheduler — fully automated daily pipeline

---

## Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Local LLM | LM Studio + Qwen 2.5 14B |
| Browser automation | Playwright + Firefox |
| Data store | Google Sheets API |
| Email | Gmail API + OAuth2 |
| Notifications | Telegram Bot API |
| Scheduler | Windows Task Scheduler + PowerShell |

---

## Quick Start

```bash
git clone https://github.com/MarcosAlvaradoD/ai-job-foundry.git
cd ai-job-foundry
pip install -r requirements.txt
playwright install firefox
cp .env.example .env
# Fill: Gmail OAuth, Google Sheets ID, Telegram token, LM Studio URL
py scripts/maintenance/run_maintenance.py
```

---

## Main Commands

```bash
# Maintenance: enrich + dedup + clean + score
py scripts/maintenance/run_maintenance.py

# Check readiness before applying
py scripts/apply/check_apply_readiness.py

# Generate cover letters (FIT >= 8)
py scripts/apply/generate_cover_letters.py --min 8

# Auto-apply
py scripts/apply/run_autoapply.py --dry-run
py scripts/apply/run_autoapply.py --submit --max 10

# Morning summary to Telegram
py scripts/morning_summary.py
```

---

## Automation Schedule

| Time | Task |
|---|---|
| 07:00 | morning_summary — daily digest to Telegram |
| 09:00 | maintenance — enrich, dedup, clean, score |
| 12:00 | fit_scores — score any unscored listings |
| Weekly | deep_clean — remove long-expired postings |

One-time setup (run as Admin): `.\scripts\setup_daily_tasks.ps1`

---

## Why Local AI?

**Privacy** — resume and job history never leave your machine.

**No API costs** — 0 cents per inference. Score 271 jobs daily, generate cover letters, zero billing.

**RTX 4090 capable** — Qwen 2.5 14B at full speed locally. Fast enough for batch pipelines.

---

## Built by

**Marcos Alberto Alvarado De La Torre** — PM / BA / Automation engineer — Mexico

> Built out of necessity. Tired of applying manually. Let the machine hunt.

---

*271 jobs tracked. Pipeline running daily.*
