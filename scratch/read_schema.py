import sqlite3
import os

db_path = os.path.join('db', 'medierp_v2.db')
conn = sqlite3.connect(db_path)
schema = conn.execute("SELECT sql FROM sqlite_master WHERE name='users'").fetchone()[0]
print(schema)
conn.close()
