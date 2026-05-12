
import subprocess
import sys

def fix():
    print("Tentative de réparation de l'environnement Python...")
    try:
        # Utiliser python -m pip pour plus de fiabilité
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "numpy<2.0.0", "scikit-learn", "joblib"])
        print("✅ Environnement mis à jour avec succès.")
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {e}")

if __name__ == "__main__":
    fix()
