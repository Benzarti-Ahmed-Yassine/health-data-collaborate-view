import sys
import os

# Ajouter src au path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.security import SecurityManager

def verify():
    sm = SecurityManager()
    
    # Tester avec un utilisateur connu (yassine.admin@medierp.ai)
    # Le password hashé en base pour cet utilisateur est celui de 'yassine' (master password précédent)
    # Hash pour 'yassine' : $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G
    
    print("Testing authentication for yassine.admin@medierp.ai...")
    user = sm.authenticate("yassine.admin@medierp.ai", "yassine")
    
    if user:
        print(f"✅ Auth Success: {user['full_name']} ({user['role']})")
        print(f"Token: {user['token'][:20]}...")
    else:
        print("❌ Auth Failed")

    # Tester le password policy
    print("\nTesting password policy for ADMIN (min 16 chars)...")
    is_valid = sm.validate_password_strength("Short1", "ADMIN")
    print(f"Short1 valid? {is_valid}")
    
    is_valid = sm.validate_password_strength("ThisIsALongEnoughPassword123", "ADMIN")
    print(f"Long password valid? {is_valid}")

if __name__ == "__main__":
    verify()
