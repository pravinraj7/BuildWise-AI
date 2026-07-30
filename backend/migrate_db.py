import sqlite3

def run_migration():
    conn = sqlite3.connect("buildwise.db")
    cursor = conn.cursor()

    columns_to_add = [
        ("building_type", "VARCHAR(100) DEFAULT 'office'"),
        ("health_score", "INTEGER DEFAULT 100"),
        ("is_active", "BOOLEAN DEFAULT 1")
    ]

    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE buildings ADD COLUMN {col_name} {col_type}")
            print(f"Successfully added column '{col_name}' to 'buildings' table.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print(f"Column '{col_name}' already exists.")
            else:
                print(f"Error adding column '{col_name}': {e}")

    conn.commit()
    conn.close()
    print("Migration finished!")

if __name__ == "__main__":
    run_migration()
