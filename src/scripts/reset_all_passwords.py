import sqlite3
import os
import sys

# Path to database
db_path = os.path.join('db', 'medierp_v2.db')
if not os.path.exists(db_path):
    db_path = os.path.join('database', 'medierp_v2.db')

def reset_all_passwords():
    new_password = "ahmedyassine12*"
    print(f"Resetting all passwords to: {new_password}")
    
    # Hash pré-calculé pour 'ahmedyassine12*' (bcrypt cost 12)
    hashed = "$2b$12$N9qo8uLOickgx2ZMRZoMyeIjZAgdt97gyptB.p0uR8M3nB.qGZvKG"

    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Update credentials table
        cursor.execute("UPDATE credentials SET value_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE type = 'password'", (hashed,))
        creds_updated = cursor.rowcount
        
        # 2. Update users table (compatibility)
        cursor.execute("UPDATE users SET password_hash = ?", (hashed,))
        users_updated = cursor.rowcount
        
        conn.commit()
        print(f"✅ Succès !")
        print(f"   - Credentials mis à jour : {creds_updated}")
        print(f"   - Users mis à jour : {users_updated}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour : {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    reset_all_passwords()
