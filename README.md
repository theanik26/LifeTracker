# LifeTrack

> **Measure Your Progress, Not Your Comparisons.**

LifeTrack is a production-ready, premium offline-first web application designed to help you build consistency by tracking daily progress across five critical categories. Instead of generic checkmarks, LifeTrack blends deep glassmorphic dark-theme aesthetics, physics-based canvas animations, and detailed database ledgers to deliver an executive tracking experience.

---

## 🌟 Key Features

- **Daily Reflection Ledger**: Track 5 core areas daily (Study, Projects, Exercise, Career build, and Distraction limits) with optional qualitative notes.
- **Perfect Day Celebrations**: Physics-based, fully offline canvas confetti animation triggered upon perfect daily check-ins.
- **Interactive 30-Day Grid**: Visual calendar representation marking logs (Green for Completed, Yellow for Partial, Red for Missed, and Slate for Pending). Click any day to see details inside glass modals.
- **Deep Performance Analytics**: High-fidelity dark mode charts powered by Chart.js (Daily trends, Habit rates, Weekday heatmaps, and habit profiles).
- **Automated Monthly Reports**: Textual habit audits with action items and key metrics (Consistency grade, best/worst week averages).
- **Offline Integrity**: SQLite storage under SQLAlchemy ORM. Zero cloud tracking, zero online authentication, completely private.
- **Portability Controls**:
  - Download formatted Excel spreadsheets (`.xlsx`) via `openpyxl`.
  - Stream clean CSV files.
  - Download executive-styled ReportLab PDF reports.
  - Export/Import JSON database backup archives.
  - Clone local copies of active SQLite files.

---

## 📁 Project Structure

```text
LifeTrack/
├── app.py                  # Flask Application Factory & Launcher
├── run.bat                 # One-click Windows Launcher script
├── requirements.txt        # Backend dependencies
├── README.md               # User documentation
├── database/
│   └── connection.py       # SQLAlchemy db instantiation
├── models/
│   └── log.py              # DailyLog database model
├── routes/
│   ├── main.py             # View controllers (Dashboard, Logs, Reports)
│   └── api.py              # REST API controllers (Submissions, Backups, Data)
├── utils/
│   ├── analytics.py        # Streak, average score, and recommendation helpers
│   ├── backup.py           # DB cloning & JSON backup actions
│   └── export.py           # CSV, Excel, and ReportLab PDF exporters
├── templates/
│   ├── base.html           # Master layout with sidebar navigation
│   ├── dashboard.html      # Habit metrics and calendar grid
│   ├── log.html            # Questionnaire wizard & celebration overlay
│   ├── analytics.html      # Visual metrics dashboard
│   ├── reports.html        # printable ledger summaries
│   └── settings.html       # Backup import/export & debug controls
└── static/
    ├── css/
    │   └── style.css       # Custom stylesheet (Glassmorphism, animations)
    └── js/
        ├── main.js         # Toast system & global actions
        ├── confetti.js     # Physics canvas confetti system
        ├── log.js          # Form wizard handler
        ├── dashboard.js    # Calendar grid renderer & modals
        └── analytics.js    # Chart.js render configurations
```

---

## ⚡ Quick Start (Windows One-Click)

LifeTrack is equipped with a launcher that automates virtual environment configurations:

1. Double-click the `run.bat` file in the project root.
2. The script will:
   - Check if Python is installed.
   - Automatically configure a virtual environment (`.venv`) if not present.
   - Install required packages (Flask, SQLAlchemy, openpyxl, reportlab).
   - Automatically open the system browser to `http://127.0.0.1:5000/`.
   - Boot up the Flask server in the console window.
3. Keep the console window open while using the application. To close the app, simply exit the console window.

---

## 🛠️ Manual Installation (Cross-Platform)

If you prefer to start the server manually or are running on macOS/Linux:

1. **Clone/Navigate** to the repository:
   ```bash
   cd LifeTrack
   ```

2. **Create and Activate a Virtual Environment**:
   * Windows:
     ```bash
     python -m venv .venv
     .venv\Scripts\activate
     ```
   * macOS/Linux:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install Dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Launch Application**:
   ```bash
   python app.py
   ```
5. Open your browser and navigate to `http://127.0.0.1:5000/`.

---

## 📝 Developer Tools

To help you review the application, we've included developer diagnostic tools in the **Backup & Data** tab:
- **Populate 30-Day Logs**: Populates synthetic habit records (mix of perfect days, partial check-ins, and missed days) spanning the past 30 days. This immediately lights up the calendar grid and charts.
- **Wipe Database Ledger**: Clears the SQLite database cleanly to test a blank state.

---

## ⚖️ License

Distributed under the MIT License. See `LICENSE` for details.
