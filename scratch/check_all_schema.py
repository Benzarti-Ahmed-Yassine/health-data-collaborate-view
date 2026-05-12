import sqlite3
conn = sqlite3.connect('db/medierp_v2.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
for t in tables:
    print(f"\n--- Table: {t} ---")
    cursor.execute(f"PRAGMA table_info({t})")
    for col in cursor.fetchall():
        print(col)
