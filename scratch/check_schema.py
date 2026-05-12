import sqlite3
conn = sqlite3.connect('db/medierp_v2.db')
cursor = conn.cursor()
cursor.execute("SELECT sql FROM sqlite_master WHERE name='notifications'")
print("--- Notifications ---")
print(cursor.fetchone()[0])
cursor.execute("SELECT sql FROM sqlite_master WHERE name='messages'")
print("\n--- Messages ---")
print(cursor.fetchone()[0])
