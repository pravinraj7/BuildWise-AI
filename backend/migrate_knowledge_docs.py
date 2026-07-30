import sqlite3

def run_migration():
    conn = sqlite3.connect("buildwise.db")
    cursor = conn.cursor()

    columns_to_add = [
        ("description", "TEXT"),
        ("file_name", "VARCHAR(255)"),
        ("file_url", "VARCHAR(500)"),
        ("file_size_bytes", "INTEGER"),
        ("document_type", "VARCHAR(50) DEFAULT 'manual'"),
        ("equipment_type", "VARCHAR(100)"),
        ("is_indexed", "BOOLEAN DEFAULT 0"),
        ("indexed_at", "DATETIME"),
        ("chroma_collection_id", "VARCHAR(100)"),
        ("tags", "JSON")
    ]

    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE knowledge_documents ADD COLUMN {col_name} {col_type}")
            print(f"Successfully added column '{col_name}' to 'knowledge_documents' table.")
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
