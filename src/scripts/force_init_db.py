import sqlite3
import os

# Path to database
db_path = os.path.join('database', 'medierp_v2.db')
schema_path = os.path.join('database', 'schema.sql')
migration_path = os.path.join('database', 'migrations', 'migration_rbac.sql')

def init_db():
    print(f"Initialisation de {db_path}...")
    
    # Ensure database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = OFF;")
    
    # 1. Load Schema
    with open(schema_path, 'r', encoding='utf-8') as f:
        content = f.read().replace("PRAGMA foreign_keys = ON;", "PRAGMA foreign_keys = OFF;")
        cursor.executescript(content)
    
    # 2. Load Migration RBAC
    with open(migration_path, 'r', encoding='utf-8') as f:
        content = f.read().replace("PRAGMA foreign_keys = ON;", "PRAGMA foreign_keys = OFF;")
        cursor.executescript(content)
        
    conn.commit()
    conn.close()
    print("✅ Base de données initialisée avec succès !")

if __name__ == "__main__":
    init_db()
