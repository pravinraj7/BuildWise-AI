import sqlite3

conn = sqlite3.connect("buildwise.db")
cursor = conn.cursor()

technician_cols = [
    ("avatar_url", "VARCHAR(512)"),
    ("specialization", "VARCHAR(255)"),
    ("total_jobs", "INTEGER DEFAULT 0"),
    ("completed_jobs", "INTEGER DEFAULT 0"),
    ("avg_resolution_time_hours", "REAL DEFAULT 0.0"),
    ("current_location", "VARCHAR(255)"),
    ("shift_start", "VARCHAR(10) DEFAULT '09:00'"),
    ("shift_end", "VARCHAR(10) DEFAULT '18:00'"),
    ("work_days", "TEXT"),
]

for col_name, col_type in technician_cols:
    try:
        cursor.execute(f"ALTER TABLE technicians ADD COLUMN {col_name} {col_type}")
        print(f"Added: {col_name}")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
            print(f"Already exists: {col_name}")
        else:
            print(f"Error: {col_name} -> {e}")

conn.commit()
conn.close()
print("Done!")
