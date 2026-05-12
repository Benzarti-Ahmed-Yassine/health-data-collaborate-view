import subprocess
import sys
import time

print("🏥 Démarrage de la Clinique Virtuelle...")
print("Patientez, ouverture de 3 fenêtres de l'application...")

# Fenêtre 1 : Secrétaire
subprocess.Popen([sys.executable, "main.py"])
time.sleep(1.5)

# Fenêtre 2 : Assistant
subprocess.Popen([sys.executable, "main.py"])
time.sleep(1.5)

# Fenêtre 3 : Docteur
subprocess.Popen([sys.executable, "main.py"])

print("✅ Terminé ! 3 fenêtres ont été ouvertes sur votre écran.")
print("👉 Connectez-vous dans chacune d'elles avec les comptes suivants :")
print("  1. yassine.secretary@medierp.ai")
print("  2. yassine.assistant@medierp.ai")
print("  3. yassine.doctor@medierp.ai")
