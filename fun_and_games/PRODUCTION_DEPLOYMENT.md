# 🚀 Fun and Games - Production Deployment Guide

## Prerequisites
- Access to Rancher console for your K8s cluster
- Fun and Games app already deployed to the cluster
- Bench console access through Rancher

## 📋 Deployment Checklist

### Step 1: Verify App Installation
```bash
# In Rancher console, access the bench container and run:
bench --site [your-site-name] list-apps
# Verify "fun_and_games" appears in the list
```

### Step 2: Prepare Excel File for Questions Import
Download the questions Excel file from development or create one with these columns:

**Required Excel Columns:**
- `question_text` - The actual question
- `category` - Fun, Professional, Technical, Personality, Leadership, Teamwork, Creative, Work Habits
- `is_active` - 1 (always set to 1)
- `for_backend_track` - 1 or 0
- `for_frontend_track` - 1 or 0
- `for_leadership_track` - 1 or 0
- `for_custom_sessions` - 1 (always set to 1)

### Step 3: Import Questions via Excel
```bash
# Method 1: Via Frappe UI (Recommended)
1. Go to your Frappe site: https://your-domain
2. Navigate to: Game Question doctype
3. Click "Menu" → "Import"
4. Upload your Excel file
5. Map columns correctly
6. Click "Import"

# Method 2: Via Console (if UI not available)
# First upload Excel file to server, then:
bench --site [your-site-name] console
>>> from frappe.utils.data_import import import_doc
>>> import_doc("Game Question", "/path/to/questions.xlsx", overwrite=True)
>>> exit()
```

### Step 4: Create Team Sessions (Flexible & Dynamic)
```bash
# Copy the session creation script to your server first, then:
bench --site [your-site-name] execute fun_and_games.create_production_sessions.create_team_sessions

# This will create 3 sessions with ALL questions matching each track:
# 1. Backend Security DevOps Session (ALL backend questions + participants)
# 2. Frontend UI UX Session (ALL frontend questions + participants)
# 3. Management Scrum Session (ALL leadership questions + participants)

# Verify sessions created:
bench --site [your-site-name] execute fun_and_games.create_production_sessions.verify_setup

# Optional: Create custom sessions with ALL questions:
# bench --site [your-site-name] console
# >>> from fun_and_games.create_production_sessions import create_custom_session
# >>> participants = [{"participant_name": "John", "team": "Backend"}, {"participant_name": "Jane", "team": "Frontend"}]
# >>> create_custom_session("My Custom Session", "Custom description", participants)
```

### Step 5: Verify Setup
```bash
# Check questions count:
bench --site [your-site-name] console
>>> frappe.db.count('Game Question')
# Should return 89

# Check sessions:
>>> frappe.db.get_all('Game Session', fields=['session_name', 'status'])
# Should show 3 sessions: Backend Security DevOps, Frontend UI UX, Management Scrum

# Check participants:
>>> frappe.db.get_all('Session Participant', fields=['participant_name', 'team'])
# Should show participants for each session

>>> exit()
```

## 🎮 Post-Deployment Usage

### Access the Application
- **Admin Panel**: `https://your-domain/admin`
- **Voting Page**: `https://your-domain/vote`
- **Results Page**: `https://your-domain/results`

### Quick Start Guide
1. **Go to Admin Panel** (`/admin`)
2. **Start a Session** - Click "Start" on any of the 3 pre-configured sessions
3. **Activate Questions** - Click "Activate" on questions to start voting
4. **Players Vote** - Share `/vote` URL with participants
5. **View Results** - Check `/results` for live results

## 🔧 Troubleshooting

### If Questions Import Fails:
```bash
# Check for errors:
bench --site [your-site-name] console
>>> frappe.db.get_all('Error Log', filters={'creation': ['>', '2025-01-01']}, limit=5)

# Manual import alternative:
>>> import json
>>> with open('/home/frappe/frappe-bench/apps/fun_and_games/questions.json', 'r') as f:
>>>     questions = json.load(f)
>>> len(questions)  # Should be 89
>>> exit()
```

### If Sessions Creation Fails:
```bash
# Check existing sessions:
bench --site [your-site-name] console
>>> frappe.db.get_all('Game Session')

# Clear and recreate if needed:
>>> frappe.db.sql("DELETE FROM `tabGame Session`")
>>> frappe.db.sql("DELETE FROM `tabSession Participant`")
>>> frappe.db.sql("DELETE FROM `tabSession Question`")
>>> frappe.db.commit()
>>> exit()

# Then re-run the creation script
```

### If App Pages Don't Load:
```bash
# Clear cache:
bench --site [your-site-name] clear-cache

# Restart services:
bench restart
```

## 📁 Required Files for Production

**Files to copy to production:**
1. `questions_import_template.csv` - Excel/CSV file with 89 questions
2. `create_production_sessions.py` - Script to create team sessions

**File locations on server:**
```
/home/frappe/frappe-bench/apps/fun_and_games/
├── questions_import_template.csv     # Questions for Excel import
├── create_production_sessions.py     # Session creation script
├── www/
│   ├── admin.html                   # Admin interface
│   ├── vote.html                    # Voting interface
│   └── results.html                 # Results display
└── fun_and_games/
    └── api.py                       # Backend APIs
```

## 🚨 Critical Notes
- **Replace `[your-site-name]`** with your actual Frappe site name
- **Run commands in sequence** - don't skip steps
- **Verify each step** before proceeding to the next
- **Check logs** if any step fails
- **Backup database** before running import scripts in production

## 🎯 Success Indicators
- ✅ 89 questions imported
- ✅ 3 sessions created (Backend, Frontend, Management)
- ✅ 9 participants added across sessions
- ✅ Admin page loads and shows sessions
- ✅ Vote page loads and shows "No active session" initially
- ✅ Results page loads

## 📞 Support
If deployment fails, check:
1. Frappe logs in Rancher
2. Database connectivity
3. File permissions in app directory
4. Site name correctness
