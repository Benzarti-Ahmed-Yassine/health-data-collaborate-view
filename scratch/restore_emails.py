import sqlite3
import os

db_path = os.path.join('db', 'medierp_v2.db')

def restore_standard_emails_safe():
    try:
        conn = sqlite3.connect(db_path, timeout=10)
        cursor = conn.cursor()
        
        # 1. Mettre des emails temporaires pour éviter les conflits
        cursor.execute("UPDATE users SET email = 'temp_' || id || '@medierp.ai'")
        
        # 2. Rétablir les emails standards
        cursor.execute("UPDATE users SET email = 'admin@medierp.ai' WHERE id = 1")
        cursor.execute("UPDATE users SET email = 'doctor@medierp.ai' WHERE id = 2")
        cursor.execute("UPDATE users SET email = 'secretary@medierp.ai' WHERE id = 3")
        cursor.execute("UPDATE users SET email = 'assistant@medierp.ai' WHERE id = 4")
        
        conn.commit()
        conn.close()
        print("RESTAURATION SUCCES: Emails standards rétablis sans conflits.")
        return True
    except Exception as e:
        print(f"ERREUR: {e}")
        return False

if __name__ == "__main__":
    restore_standard_emails_safe()
