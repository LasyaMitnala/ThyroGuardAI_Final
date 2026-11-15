# ThyroGuard — Phase 1 foundation

A local Streamlit prototype for thyroid monitoring and risk-awareness workflows.

## Requirements
- Python 3.10 or newer
- VS Code
- Git (recommended)

## Setup (macOS)
```bash
cd thyroguard
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501 if the browser does not open automatically.

## Phase 1 includes
- Premium clinical visual shell and navigation
- Four module pages plus reports page
- Local SQLite database and fictional demo records
- Basic trend visualizations
- Shared data access layer

## Safety and scope
This is an educational prototype using fictional data. It is not validated for clinical use and does not diagnose, predict medical outcomes, or recommend treatment. Do not enter identifiable patient data.

## Git
```bash
git init
git add .
git commit -m "Build ThyroGuard Phase 1 foundation"
```

The SQLite database is excluded from Git by `.gitignore`.


## Phase 2 — Patient Management
- Create, edit, and archive local patient profiles.
- Switch active patient from the sidebar.
- Existing demo records remain associated with Demo Patient A.
- Existing databases are migrated automatically when the app starts.

Use fictional profiles only. Do not enter identifiable or real patient health data.


## ThyroidTrend — Functional laboratory workflow
- Add TSH, FT4 and FT3 panels for the selected patient.
- Store each panel and the report-specific reference intervals in SQLite.
- Compare the latest panel with its entered intervals.
- Visualize longitudinal measurements and compare consecutive panels.
- Review and remove incorrectly entered records.
- The current analytical summaries are transparent calculations, not a trained diagnostic AI model.


## SymptomWatch — Functional symptom workflow
- Record patient-reported energy, fatigue, concentration, memory and sleep ratings.
- Save dated check-ins to the selected patient's SQLite record.
- Compare selected symptom dimensions over time.
- Review latest ratings and transparent changes since the previous check-in.
- Review whether symptom and laboratory records share dates, without implying causation.
- Remove incorrectly entered check-ins.
- AI pattern recognition is planned for a later, separately validated integration stage.
