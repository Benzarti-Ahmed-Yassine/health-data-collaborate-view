import sqlite3
import os

db_path = os.path.join('db', 'medierp_v2.db')

def update_emails_final():
    try:
        conn = sqlite3.connect(db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        users = cursor.execute("SELECT id, role FROM users").fetchall()
        
        for user in users:
            # On utilise l'ID pour garantir l'unicité
            new_email = f"benzartiahmedyassine+{user['id']}@gmail.com"
            cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user['id']))
            
        conn.commit()
        conn.close()
        print("SUCCES: Tous les comptes mis a jour avec benzartiahmedyassine+ID@gmail.com")
        return True
    except Exception as e:
        print(f"ERREUR: {e}")
        return False

if __name__ == "__main__":
    update_emails_final()
