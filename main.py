"""
Smart Medical AI - Point d'entrée de production
"""

import sys
import os
from src.utils.qt_compat import QtWidgets, QtCore
from src.core.app import create_app
from src.core.theme_manager import initialize_theme_manager, ThemeType
from src.views.login_view import LoginDialog
from src.views.main_window import MainWindow

def main():
    # 1. Initialisation Application
    app = create_app()
    app.setQuitOnLastWindowClosed(False) # Prevent app from quitting when login closes

    # 2. Initialize Theme Manager
    theme_manager = initialize_theme_manager(app, ThemeType.LIGHT)
    
    while True:
        # 2. Lancement du Login MediERP
        login = LoginDialog()
        if login.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            # Authentification réussie
            user = login.get_user()
            if not user:
                continue
                
            app.set_current_user(user)
            
            # 3. Lancement Main Window (RBAC activé)
            window = MainWindow()
            window.show()
            
            # On attend que la fenêtre se ferme.
            app.setQuitOnLastWindowClosed(True) # Re-enable for the main window
            app.exec()
            
            # Si l'utilisateur est déconnecté (current_user est None), on reboucle sur le login.
            if app.current_user is None:
                app.setQuitOnLastWindowClosed(False) # Prepare for next login
                continue
            else:
                break
        else:
            # Annulation ou échec
            print("[Main] Connexion annulée ou échouée.")
            break
    
    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[FATAL] Crash au démarrage: {e}")
        import traceback
        traceback.print_exc()