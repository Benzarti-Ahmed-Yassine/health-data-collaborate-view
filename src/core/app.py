"""
Smart Medical AI — app.py
Application Core avec intégration Antigravity RBAC + migration automatique
"""

import sys
import os
from pathlib import Path
from typing import Any

from ..utils.qt_compat import QtWidgets, QtCore, QtGui

from .database import DatabaseManager
from .security import SecurityManager
from .events import EventBus, EventType
from .rbac import AntigravityRBAC


class SmartMedicalApp(QtWidgets.QApplication):
    """
    Application principale Smart Medical AI.
    Expose: db, security, rbac, events, current_user
    """
    _instance = None

    def __new__(cls, argv=None):
        if cls._instance is None:
            if hasattr(QtCore.Qt.HighDpiScaleFactorRoundingPolicy, "PassThrough"):
                QtWidgets.QApplication.setHighDpiScaleFactorRoundingPolicy(
                    QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
                )
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, argv=None):
        if hasattr(self, "_initialized_instance") and self._initialized_instance:
            return
        if argv is None:
            argv = sys.argv
        super().__init__(argv)
        self._initialized_instance = True

        # Force Light Mode — must be called AFTER super().__init__()
        self.setStyle(QtWidgets.QStyleFactory.create("Fusion"))
        light_palette = QtGui.QPalette()
        light_palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(255, 255, 255))
        light_palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor(0, 80, 179))
        light_palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(255, 255, 255))
        light_palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(248, 249, 250))
        light_palette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtGui.QColor(255, 255, 255))
        light_palette.setColor(QtGui.QPalette.ColorRole.ToolTipText, QtGui.QColor(0, 80, 179))
        light_palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor(0, 80, 179))
        light_palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(255, 255, 255))
        light_palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(0, 80, 179))
        light_palette.setColor(QtGui.QPalette.ColorRole.BrightText, QtGui.QColor(255, 255, 255))
        light_palette.setColor(QtGui.QPalette.ColorRole.Link, QtGui.QColor(24, 144, 255))
        light_palette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(24, 144, 255))
        light_palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(255, 255, 255))
        self.setPalette(light_palette)

        self.setApplicationName("Smart Medical AI")
        self.setApplicationVersion("2.0.0")
        self.setOrganizationName("MediERP")

        self.db: DatabaseManager = None
        self.security: SecurityManager = None
        self.rbac: AntigravityRBAC = None
        self.events: EventBus = None
        self.current_user: dict = None
        self.active_patient_id: int = None

        self._initialized = False

    def initialize(self) -> bool:
        if self._initialized:
            return True

        try:
            print("[App] Initialisation Smart Medical AI v2.0 (Antigravity RBAC)...")

            # 1. Base de données
            self.db = DatabaseManager()

            # 2. Migrations (ordre : sécurité → RBAC → assistant → v4_complete)
            migrations_dir = Path(__file__).parent.parent.parent / "database" / "migrations"
            migration_order = [
                "migration_v3_security.sql",  # credentials, credential_audit
                "migration_rbac.sql",          # rôles, permissions, user_roles
                "migration_assistant.sql",     # tasks, inventory
                "migration_v4_complete.sql",   # arrived, reminder_sent, messages, etc.
                "005_feature_updates.sql",     # deposits, material requests
                "006_fix_messages_v2.sql",    # fix messages table schema
                "007_messages_and_notifications.sql",  # messages + notifications
                "008_system_config.sql",               # system configuration
            ]
            for migration_file in migration_order:
                mp = migrations_dir / migration_file
                if mp.exists():
                    self.db.apply_migration(str(mp))
                else:
                    print(f"[App] ⚠️  Migration introuvable: {migration_file}")

            # 3. Moteur RBAC
            self.rbac = AntigravityRBAC(self.db)

            # 4. Sécurité
            self.security = SecurityManager()

            # 5. Events
            self.events = EventBus()

            # 6. Vérification intégrité audit
            if not self.security.verify_audit_chain():
                print("[App] ⚠️  ALERTE SÉCURITÉ : L'intégrité de l'audit est compromise !")
            else:
                print("[App] ✅ Intégrité de l'audit vérifiée.")

            # 7. Services d'arrière-plan
            from ..services.reminder_service import reminder_service
            reminder_service.start()

            # 8. Style & Fonts (Now handled by ThemeManager)
            # The ThemeManager is initialized in main.py with the app instance
            self._configure_fonts()

            self._initialized = True
            print("[App] ✅ Initialisation complète.")
            return True

        except Exception as e:
            print(f"[App] ERREUR initialisation: {e}")
            import traceback
            traceback.print_exc()
            return False

    # def _load_stylesheet(self) -> None:
    #     """Deprecated: Stylesheet is now managed by ThemeManager."""
    #     # style_path = Path(__file__).parent.parent.parent / "config" / "styles.qss"
    #     # if style_path.exists():
    #     #     with open(style_path, "r") as f:
    #     #         self.setStyleSheet(f.read())

    def _configure_fonts(self) -> None:
        font = QtGui.QFont("Segoe UI", 10)
        font.setStyleHint(QtGui.QFont.StyleHint.SansSerif)
        self.setFont(font)

    # ================================================================
    # GESTION UTILISATEUR COURANT
    # ================================================================

    def set_current_user(self, user_data: dict) -> None:
        """Définit l'utilisateur connecté et émet l'événement login."""
        self.current_user = user_data
        if user_data:
            # Enrichir avec permissions depuis RBAC
            user_id = user_data.get("user_id") or user_data.get("id")
            if user_id and self.rbac:
                user_data["permissions"] = self.rbac.get_user_permissions(user_id)
                user_data["role_level"] = self.rbac.get_user_level(user_id)
            self.events.emit(EventType.USER_LOGIN, user_data)

    def logout(self) -> None:
        if self.current_user:
            self.events.emit(EventType.USER_LOGOUT, self.current_user)
            # Invalider cache RBAC
            if self.rbac and self.current_user:
                uid = self.current_user.get("user_id") or self.current_user.get("id")
                if uid:
                    self.rbac.invalidate_cache(uid)
            self.current_user = None

    # ================================================================
    # HELPERS PERMISSION (raccourci pour les vues)
    # ================================================================

    def has_permission(self, permission_id: str) -> bool:
        """Vérifie si l'utilisateur courant a une permission."""
        if not self.current_user or not self.rbac:
            return False
        uid = self.current_user.get("user_id") or self.current_user.get("id")
        if not uid:
            return False
        return self.rbac.has_permission(uid, permission_id)

    def current_role(self) -> str:
        """Retourne le rôle de l'utilisateur courant."""
        if not self.current_user:
            return "UNKNOWN"
        return self.current_user.get("role", "UNKNOWN")

    def current_user_id(self) -> int:
        """Retourne l'ID de l'utilisateur courant."""
        if not self.current_user:
            return None
        return self.current_user.get("user_id") or self.current_user.get("id")

    # ================================================================
    # CONFIGURATION SYSTEME
    # ================================================================

    def get_config(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur de configuration depuis la base de données."""
        try:
            row = self.db.fetch_one("SELECT value FROM system_config WHERE key = ?", (key,))
            return row["value"] if row else default
        except Exception:
            return default

    def set_config(self, key: str, value: Any) -> bool:
        """Définit une valeur de configuration dans la base de données."""
        try:
            self.db.execute(
                "INSERT OR REPLACE INTO system_config (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                (key, str(value))
            )
            return True
        except Exception as e:
            print(f"[App] Erreur set_config: {e}")
            return False

    # ================================================================
    # SINGLETON
    # ================================================================

    @classmethod
    def get_instance(cls) -> "SmartMedicalApp":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


def create_app() -> SmartMedicalApp:
    app = SmartMedicalApp()
    app.initialize()
    return app
