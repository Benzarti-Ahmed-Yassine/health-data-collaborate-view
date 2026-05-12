import sqlite3
import os

# Path to database
db_path = os.path.join('database', 'medierp_v2.db')

def seed():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Password hash for 'ahmedyassine12*' (bcrypt)
    pwd_hash = '$2b$12$N9qo8uLOickgx2ZMRZoMyeIjZAgdt97gyptB.p0uR8M3nB.qGZvKG'
    
    users = [
        ('admin@medierp.ai', pwd_hash, 'Super Administrateur', 'ADMIN'),
        ('doctor@medierp.ai', pwd_hash, 'Dr. Ahmed Yassine', 'DOCTOR'),
        ('secretary@medierp.ai', pwd_hash, 'Marie Secrétaire', 'SECRETARY'),
        ('assistant@medierp.ai', pwd_hash, 'Karim Assistant', 'ASSISTANT')
    ]
    
    for email, phash, name, role in users:
        cursor.execute("""
            INSERT OR REPLACE INTO users (email, password_hash, full_name, role, is_active)
            VALUES (?, ?, ?, ?, 1)
        """, (email, phash, name, role))
    
    # Add Test Patient
    cursor.execute("""
        INSERT OR REPLACE INTO patients (cin, first_name, last_name, is_active)
        VALUES ('A100', 'Marie', 'Lemoine', 1)
    """)
    
    conn.commit()
    conn.close()
    print("✅ Utilisateurs de test créés avec succès !")
    print("👉 Mot de passe pour tous : ahmedyassine12*")

if __name__ == "__main__":
    seed()
