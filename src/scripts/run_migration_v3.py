import sys
import os

# Ajouter src au path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.database import DatabaseManager

def run_migration():
    db = DatabaseManager()
    migration_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../database/migrations/migration_v3_security.sql"))
    
    print(f"Applying migration: {migration_path}")
    success = db.apply_migration(migration_path)
    
    if success:
        print("Migration V3 Security appliquee avec succes.")
    else:
        print("❌ Échec de la migration.")

if __name__ == "__main__":
    run_migration()
