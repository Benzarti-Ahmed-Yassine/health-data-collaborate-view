import bcrypt
import sys

def generate_credential_sql(user_id, password):
    """Génère une requête SQL INSERT pour la table credentials avec un mot de passe hashé."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    
    sql = f"-- Commande SQL pour l'utilisateur ID {user_id}\n"
    sql += f"INSERT INTO credentials (user_id, type, value_hash, is_active, created_at) \n"
    sql += f"VALUES ({user_id}, 'password', '{hashed}', 1, CURRENT_TIMESTAMP);"
    return sql

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_credentials_sql.py <user_id> <password>")
        sys.exit(1)
        
    user_id = sys.argv[1]
    password = sys.argv[2]
    print(generate_credential_sql(user_id, password))
