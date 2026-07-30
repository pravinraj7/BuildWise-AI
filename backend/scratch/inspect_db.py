import sqlite3

def inspect():
    conn = sqlite3.connect("c:/Users/pravi/Downloads/BuildwiseAI/backend/buildwise.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", tables)
    for table in tables:
        name = table[0]
        cursor.execute(f"PRAGMA table_info({name});")
        print(f"\nTable {name} info:")
        for col in cursor.fetchall():
            print(col)
    conn.close()

if __name__ == "__main__":
    inspect()
