import sqlite3
from pathlib import Path
from datetime import date, timedelta

DB_PATH = Path(__file__).resolve().parent / "thyroguard.db"

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def _columns(conn, table):
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}

def initialize_database():
    with connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            display_name TEXT NOT NULL,
            diagnosis TEXT DEFAULT 'Hypothyroidism',
            medication TEXT DEFAULT '',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS lab_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            test_date TEXT NOT NULL,
            tsh REAL, ft4 REAL, ft3 REAL,
            tsh_low REAL, tsh_high REAL,
            ft4_low REAL, ft4_high REAL,
            ft3_low REAL, ft3_high REAL,
            FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS symptom_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            entry_date TEXT NOT NULL,
            energy INTEGER, fatigue INTEGER, concentration INTEGER,
            memory INTEGER, sleep INTEGER, notes TEXT DEFAULT '',
            FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS followups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            last_test_date TEXT,
            next_review_date TEXT,
            clinician_note TEXT DEFAULT '',
            completed INTEGER DEFAULT 0,
            FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
        """)
        # Safe schema migration for databases created by earlier ThyroGuard versions.
        patient_cols = _columns(conn, "patients")
        migrations = {
            "date_of_birth": "TEXT",
            "clinician_notes": "TEXT DEFAULT ''",
            "is_active": "INTEGER DEFAULT 1",
            "updated_at": "TEXT",
        }
        for name, definition in migrations.items():
            if name not in patient_cols:
                conn.execute(f"ALTER TABLE patients ADD COLUMN {name} {definition}")

        count = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
        if count == 0:
            cur = conn.execute(
                """INSERT INTO patients(display_name, diagnosis, medication, created_at,
                   clinician_notes, is_active, updated_at) VALUES(?,?,?,?,?,?,?)""",
                ("Demo Patient A", "Hypothyroidism", "Clinician-recorded medication",
                 date.today().isoformat(), "Fictional demonstration profile.", 1, date.today().isoformat())
            )
            pid = cur.lastrowid
            today = date.today()
            labs = [
                (today - timedelta(days=120), 6.2, 1.00, 3.0),
                (today - timedelta(days=60), 4.8, 1.10, 3.2),
                (today, 3.5, 1.15, 3.3),
            ]
            for d, tsh, ft4, ft3 in labs:
                conn.execute("""INSERT INTO lab_entries
                    (patient_id,test_date,tsh,ft4,ft3,tsh_low,tsh_high,ft4_low,ft4_high,ft3_low,ft3_high)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                    (pid, d.isoformat(), tsh, ft4, ft3, 0.4, 4.0, 0.8, 1.8, 2.3, 4.2))
            for days_ago, energy, fatigue, concentration, memory, sleep in [
                (14, 2, 4, 3, 2, 3), (7, 3, 3, 3, 2, 4), (1, 3, 3, 4, 3, 3)
            ]:
                conn.execute("""INSERT INTO symptom_entries
                    (patient_id,entry_date,energy,fatigue,concentration,memory,sleep)
                    VALUES(?,?,?,?,?,?,?)""",
                    (pid, (today - timedelta(days=days_ago)).isoformat(), energy, fatigue, concentration, memory, sleep))
            conn.execute("""INSERT INTO followups(patient_id,last_test_date,next_review_date,clinician_note)
                VALUES(?,?,?,?)""",
                (pid, today.isoformat(), (today + timedelta(days=90)).isoformat(),
                 "Illustrative date only; confirm the monitoring schedule with your clinician."))

def get_dashboard_summary(patient_id=None):
    with connect() as conn:
        if patient_id is None:
            return {
                "patients": conn.execute("SELECT COUNT(*) FROM patients WHERE is_active=1").fetchone()[0],
                "labs": conn.execute("SELECT COUNT(*) FROM lab_entries").fetchone()[0],
                "symptoms": conn.execute("SELECT COUNT(*) FROM symptom_entries").fetchone()[0],
                "followups": conn.execute("SELECT COUNT(*) FROM followups").fetchone()[0],
            }
        return {
            "patients": 1,
            "labs": conn.execute("SELECT COUNT(*) FROM lab_entries WHERE patient_id=?", (patient_id,)).fetchone()[0],
            "symptoms": conn.execute("SELECT COUNT(*) FROM symptom_entries WHERE patient_id=?", (patient_id,)).fetchone()[0],
            "followups": conn.execute("SELECT COUNT(*) FROM followups WHERE patient_id=?", (patient_id,)).fetchone()[0],
        }

def get_patients(include_inactive=False):
    with connect() as conn:
        query = "SELECT * FROM patients"
        if not include_inactive:
            query += " WHERE is_active=1"
        query += " ORDER BY display_name COLLATE NOCASE"
        return [dict(row) for row in conn.execute(query)]

def get_patient(patient_id):
    with connect() as conn:
        row = conn.execute("SELECT * FROM patients WHERE id=?", (patient_id,)).fetchone()
        return dict(row) if row else None

def create_patient(display_name, diagnosis, medication="", date_of_birth=None, clinician_notes=""):
    today = date.today().isoformat()
    with connect() as conn:
        cur = conn.execute("""INSERT INTO patients
            (display_name,diagnosis,medication,date_of_birth,clinician_notes,created_at,updated_at,is_active)
            VALUES(?,?,?,?,?,?,?,1)""",
            (display_name.strip(), diagnosis, medication.strip(), date_of_birth,
             clinician_notes.strip(), today, today))
        return cur.lastrowid

def update_patient(patient_id, display_name, diagnosis, medication="", date_of_birth=None, clinician_notes=""):
    with connect() as conn:
        conn.execute("""UPDATE patients SET display_name=?, diagnosis=?, medication=?,
            date_of_birth=?, clinician_notes=?, updated_at=? WHERE id=?""",
            (display_name.strip(), diagnosis, medication.strip(), date_of_birth,
             clinician_notes.strip(), date.today().isoformat(), patient_id))

def archive_patient(patient_id):
    with connect() as conn:
        conn.execute("UPDATE patients SET is_active=0, updated_at=? WHERE id=?",
                     (date.today().isoformat(), patient_id))

def get_lab_entries(patient_id=1):
    with connect() as conn:
        return [dict(row) for row in conn.execute(
            "SELECT * FROM lab_entries WHERE patient_id=? ORDER BY test_date", (patient_id,))]

def get_symptom_entries(patient_id=1):
    with connect() as conn:
        return [dict(row) for row in conn.execute(
            "SELECT * FROM symptom_entries WHERE patient_id=? ORDER BY entry_date", (patient_id,))]

def get_followups(patient_id=1):
    with connect() as conn:
        return [dict(row) for row in conn.execute(
            "SELECT * FROM followups WHERE patient_id=? ORDER BY next_review_date", (patient_id,))]


def add_lab_entry(patient_id, test_date, tsh, ft4, ft3,
                  tsh_low, tsh_high, ft4_low, ft4_high, ft3_low, ft3_high):
    """Save one laboratory panel for a patient."""
    with connect() as conn:
        conn.execute(
            """INSERT INTO lab_entries
            (patient_id,test_date,tsh,ft4,ft3,
             tsh_low,tsh_high,ft4_low,ft4_high,ft3_low,ft3_high)
            VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (patient_id, test_date, tsh, ft4, ft3,
             tsh_low, tsh_high, ft4_low, ft4_high, ft3_low, ft3_high)
        )

def delete_lab_entry(entry_id, patient_id):
    """Delete a selected laboratory entry belonging to the active patient."""
    with connect() as conn:
        conn.execute(
            "DELETE FROM lab_entries WHERE id=? AND patient_id=?",
            (entry_id, patient_id)
        )


def add_symptom_entry(patient_id, entry_date, energy, fatigue, concentration,
                      memory, sleep, notes=""):
    """Save a patient-reported symptom check-in."""
    with connect() as conn:
        conn.execute(
            """INSERT INTO symptom_entries
            (patient_id, entry_date, energy, fatigue, concentration, memory, sleep, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (patient_id, entry_date, energy, fatigue, concentration, memory, sleep, notes.strip())
        )

def delete_symptom_entry(entry_id, patient_id):
    """Delete a symptom check-in belonging to the selected patient."""
    with connect() as conn:
        conn.execute(
            "DELETE FROM symptom_entries WHERE id=? AND patient_id=?",
            (entry_id, patient_id)
        )
