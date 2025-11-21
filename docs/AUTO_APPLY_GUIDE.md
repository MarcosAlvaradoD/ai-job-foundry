# 🤖 LinkedIn Auto-Apply V2 - Complete Guide

## 📋 Overview

Automated application system for LinkedIn Easy Apply jobs with **intelligent form filling**.

**Features:**
- ✅ Filters jobs by FIT SCORE (default: >= 7)
- ✅ Detects and fills form fields automatically
- ✅ Handles multi-step applications
- ✅ Answers common questions (work authorization, sponsorship, etc.)
- ✅ Updates status in Google Sheets
- ✅ **SAFE MODE by default** (dry-run, no actual submit)

---

## 🚀 Quick Start

### Prerequisites

1. **LinkedIn session saved in browser**
   ```powershell
   # First time: Login to LinkedIn manually
   py scripts/save_linkedin_session.py
   ```

2. **Google Sheets with jobs data**
   - Must have columns: Company, Role, FitScore, Status, ApplyURL, CreatedAt
   - Jobs with FIT >= 7 are targeted

---

## 🎯 Usage

### DRY RUN (Recommended First Time)

Fills forms but **DOES NOT submit**:

```powershell
py linkedin_auto_apply_v2.py
```

**What happens:**
1. Finds jobs with FIT >= 7
2. Opens each job in browser
3. Clicks "Easy Apply"
4. **FILLS ALL FORM FIELDS**
5. Shows "Submit" button
6. **DOES NOT CLICK SUBMIT** ✅ SAFE
7. Closes modal

---

### LIVE MODE (Real Applications)

**⚠️ WARNING: This will actually submit applications!**

Edit `linkedin_auto_apply_v2.py`:

```python
if __name__ == "__main__":
    auto_apply = LinkedInAutoApplyV2()
    
    # Change dry_run=False to enable real submit
    auto_apply.run(dry_run=False, max_applies=3, min_score=7)
```

Then run:
```powershell
py linkedin_auto_apply_v2.py
```

You'll have 5 seconds to cancel (Ctrl+C).

---

## 📝 CV Data Configuration

Edit your info in `linkedin_auto_apply_v2.py`:

```python
self.cv_data = {
    'full_name': 'Marcos Alberto Alvarado de la Torre',
    'email': 'marcos.alvarado.dltr@gmail.com',
    'phone': '+52 33 1234 5678',  # ⚠️ UPDATE THIS
    'location': 'Guadalajara, Jalisco, Mexico',
    'linkedin': 'https://www.linkedin.com/in/marcos-alvarado',
    'years_experience': '10+',
    
    # Work authorization
    'authorized_mexico': True,
    'authorized_us': False,
    'require_sponsorship': True,
    
    # Preferences
    'desired_salary': '50000',  # Monthly MXN
    'start_date': '2 weeks',
    'remote_only': True,
}
```

---

## 🔧 Advanced Options

### Change Minimum FIT Score

```python
auto_apply.run(min_score=8)  # Only jobs with FIT >= 8
```

### Limit Applications

```python
auto_apply.run(max_applies=5)  # Max 5 applications per run
```

### Combine Options

```python
auto_apply.run(
    dry_run=False,      # REAL submit
    max_applies=3,      # Max 3 jobs
    min_score=7         # FIT >= 7
)
```

---

## 📊 What Gets Filled Automatically

### Basic Info
- ✅ First Name / Last Name
- ✅ Email
- ✅ Phone
- ✅ Location / City
- ✅ LinkedIn URL

### Questions Handled
- ✅ Years of experience
- ✅ Work authorization
- ✅ Sponsorship requirement
- ✅ Relocation willingness
- ✅ Start date

### Multi-Step Forms
- ✅ Automatically clicks "Next"
- ✅ Fills each step
- ✅ Max 5 steps handled

---

## 🛡️ Safety Features

1. **DRY-RUN Default**
   - Forms are filled but NOT submitted
   - You can review everything first

2. **5-Second Cancel Window**
   - When live mode starts, you have 5 seconds to abort

3. **Browser Visible**
   - You can see exactly what's happening

4. **Status Updates**
   - Google Sheets updated even in dry-run mode

---

## 🐛 Troubleshooting

### "No high-FIT jobs found"

Check:
1. Jobs have FIT SCORE >= 7
2. Status != "applied"
3. ApplyURL contains "linkedin.com/jobs"

### "Application modal not found"

Possible causes:
- Not an Easy Apply job
- LinkedIn UI changed
- Page didn't load completely

### "Submit button not found"

- Form might have errors
- Multi-step form not completed
- LinkedIn wants manual review

---

## 📈 Best Practices

1. **Start with dry-run** to verify form filling works
2. **Apply to 3-5 jobs** per session (avoid spam detection)
3. **Space out runs** (wait 30-60 minutes between batches)
4. **Review filled forms** in dry-run before going live
5. **Keep browser visible** to catch issues

---

## 🔮 Future Enhancements

- [ ] Upload resume/CV automatically
- [ ] Handle complex questions with AI
- [ ] Cover letter auto-generation
- [ ] Application tracking dashboard
- [ ] Email confirmation monitoring

---

## ⚠️ Important Notes

- **Only works with LinkedIn Easy Apply jobs**
- **Requires LinkedIn session to be active**
- **Use responsibly** - respect platform terms of service
- **Review applications** periodically
- **Update CV data** to match your actual info

---

**Created:** 2025-11-18  
**Version:** 2.0 (Complete Implementation)  
**Status:** ✅ Fully Functional with Safety Modes
