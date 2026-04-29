# 🎨 AI JOB FOUNDRY - WEB APPLICATION

Modern web interface for AI Job Foundry automation system.

## 🚀 Quick Start

```powershell
# Install Flask (if not already)
pip install flask --break-system-packages

# Install BeautifulSoup4 (for email fix)
pip install beautifulsoup4 --break-system-packages

# Start web server
py web_app\app.py

# Open browser
# http://localhost:5000
```

## ✨ Features

### 1. Dashboard
- **Stats Cards:** Total jobs, high FIT, with URLs, avg FIT
- **Charts:** Visual breakdown by status
- **Real-time updates:** Auto-refresh every 30 seconds

### 2. Control Center
Execute commands with one click:
- Run full pipeline
- Process emails
- LinkedIn scraper
- Verify URLs
- Standardize status

### 3. Jobs Table
- View recent 10 jobs
- FIT score badges (color-coded)
- Status indicators
- Direct links to applications

### 4. System Status
Monitor health of:
- OAuth authentication
- LM Studio (AI)
- Google Sheets connection

## 📂 File Structure

```
web_app/
├── app.py              # Flask backend
├── templates/
│   └── index.html      # Main UI
└── static/             # Future: CSS/JS files
```

## 🛠️ Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** HTML + Tailwind CSS + Alpine.js
- **Charts:** Chart.js
- **Real-time:** Server-Sent Events (SSE)

## 🔧 Configuration

The web app automatically loads from your existing `.env` file:
- `GOOGLE_SHEETS_ID`
- LM Studio endpoint
- OAuth credentials

No additional configuration needed!

## 📝 API Endpoints

- `GET /` - Main dashboard
- `GET /api/jobs` - Get all jobs
- `GET /api/stats` - Get statistics
- `GET /api/status` - System status
- `POST /api/run/<command>` - Execute commands
- `GET /api/env` - Read .env
- `POST /api/env` - Update .env
- `GET /api/logs` - Stream logs (SSE)

## 🎯 Next Features (Future)

- [ ] Settings page (.env editor)
- [ ] Logs viewer (real-time)
- [ ] Interview Copilot integration
- [ ] Auto-apply UI
- [ ] Job filters and search
- [ ] Export to CSV
- [ ] Dark mode

## 🐛 Troubleshooting

**Port 5000 already in use:**
```powershell
# Kill process on port 5000
Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess -Force

# Or change port in app.py:
app.run(host='0.0.0.0', port=5001, debug=True)
```

**OAuth errors:**
```powershell
py reauthenticate_gmail_v2.py
```

**BeautifulSoup not found:**
```powershell
pip install beautifulsoup4 --break-system-packages
```

## 📞 Support

Issues? Check:
1. `docs/PROJECT_STATUS.md` - Latest project state
2. `CLAUDE_CODE_PROMPT.md` - Development guide
3. Control Center logs in `logs/powershell/`

---

**Built with ❤️ by Marcos Alvarado**  
**Last updated:** 2025-11-19 23:00 CST
