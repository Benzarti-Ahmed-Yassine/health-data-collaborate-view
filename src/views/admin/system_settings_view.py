"""
MediERP — System Settings View
Gestion dynamique des paramètres de la clinique, de la sécurité et des sauvegardes.
"""

from ...utils.qt_compat import QtWidgets, QtCore, QtGui
from ...core.app import SmartMedicalApp

class SystemSettingsView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header = QtWidgets.QLabel("⚙️ Paramètres Système")
        header.setStyleSheet("font-size: 22pt; font-weight: bold; color: #722ed1;")
        layout.addWidget(header)

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #f0f0f0; background: white; border-radius: 12px; }
            QTabBar::tab { background: #fafafa; padding: 12px 25px; border: 1px solid #f0f0f0; border-bottom: none; border-radius: 8px 8px 0 0; margin-right: 2px; }
            QTabBar::tab:selected { background: white; font-weight: bold; color: #722ed1; border-top: 3px solid #722ed1; }
        """)

        self.tabs.addTab(self._create_clinic_tab(), "🏥 Clinique")
        self.tabs.addTab(self._create_security_tab(), "🔒 Sécurité & IA")
        self.tabs.addTab(self._create_backup_tab(), "💾 Sauvegarde & Maintenance")

        layout.addWidget(self.tabs)

        # Bottom Actions
        actions = QtWidgets.QHBoxLayout()
        self.btn_save_all = QtWidgets.QPushButton("💾 Enregistrer tous les paramètres")
        self.btn_save_all.setFixedHeight(45)
        self.btn_save_all.setFixedWidth(300)
        self.btn_save_all.setStyleSheet("""
            background-color: #722ed1; color: white; border-radius: 8px; font-weight: bold; font-size: 11pt;
        """)
        self.btn_save_all.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btn_save_all.clicked.connect(self._on_save_all)
        
        actions.addStretch()
        actions.addWidget(self.btn_save_all)
        layout.addLayout(actions)

    def _create_clinic_tab(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)

        form = QtWidgets.QFormLayout()
        form.setSpacing(20)
        
        self.txt_clinic_name = QtWidgets.QLineEdit()
        self.txt_clinic_address = QtWidgets.QLineEdit()
        self.txt_clinic_phone = QtWidgets.QLineEdit()
        self.txt_clinic_email = QtWidgets.QLineEdit()
        
        form.addRow("Nom de l'établissement:", self.txt_clinic_name)
        form.addRow("Adresse physique:", self.txt_clinic_address)
        form.addRow("Téléphone:", self.txt_clinic_phone)
        form.addRow("Email de contact:", self.txt_clinic_email)
        
        layout.addLayout(form)
        layout.addStretch()
        return widget

    def _create_security_tab(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        layout.addWidget(QtWidgets.QLabel("<b>Authentification & Protection</b>"))
        
        self.check_face = QtWidgets.QCheckBox("Exiger l'authentification faciale pour le staff")
        self.check_mfa = QtWidgets.QCheckBox("Activer la double authentification (2FA) par email")
        self.check_audit = QtWidgets.QCheckBox("Forcer le chaînage Blockchain (Audit permanent)")
        
        layout.addWidget(self.check_face)
        layout.addWidget(self.check_mfa)
        layout.addWidget(self.check_audit)
        
        layout.addSpacing(20)
        layout.addWidget(QtWidgets.QLabel("<b>Intelligence Artificielle</b>"))
        self.check_auto_ia = QtWidgets.QCheckBox("Lancer l'analyse prédictive automatique lors de la consultation")
        self.check_auto_ia.setChecked(True)
        layout.addWidget(self.check_auto_ia)
        
        layout.addStretch()
        return widget

    def _create_backup_tab(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        # Maintenance Section
        layout.addWidget(QtWidgets.QLabel("<b>État du Système</b>"))
        self.check_maintenance = QtWidgets.QCheckBox("Activer le Mode Maintenance")
        self.check_maintenance.setStyleSheet("color: #f5222d; font-weight: bold;")
        lbl_maint = QtWidgets.QLabel("Si activé, seuls les administrateurs pourront se connecter.")
        lbl_maint.setStyleSheet("color: #8c8c8c; font-size: 9pt; margin-left: 25px;")
        
        layout.addWidget(self.check_maintenance)
        layout.addWidget(lbl_maint)

        layout.addSpacing(20)
        
        # Backup Section
        layout.addWidget(QtWidgets.QLabel("<b>Sauvegarde des Données</b>"))
        self.check_auto_backup = QtWidgets.QCheckBox("Activer la sauvegarde automatique quotidienne")
        
        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addWidget(QtWidgets.QLabel("Intervalle (Heures) :"))
        self.sb_backup_interval = QtWidgets.QSpinBox()
        self.sb_backup_interval.setRange(1, 168)
        self.sb_backup_interval.setFixedWidth(80)
        h_layout.addWidget(self.sb_backup_interval)
        h_layout.addStretch()
        
        layout.addWidget(self.check_auto_backup)
        layout.addLayout(h_layout)
        
        layout.addSpacing(10)
        btn_manual_backup = QtWidgets.QPushButton("🚀 Lancer une sauvegarde immédiate")
        btn_manual_backup.setFixedWidth(250)
        btn_manual_backup.clicked.connect(self._manual_backup)
        layout.addWidget(btn_manual_backup)

        layout.addStretch()
        return widget

    def _load_settings(self):
        """Charge les paramètres depuis la base de données."""
        # Clinique
        self.txt_clinic_name.setText(self.app.get_config("clinic_name", "MediERP Medical Center"))
        self.txt_clinic_address.setText(self.app.get_config("clinic_address", ""))
        self.txt_clinic_phone.setText(self.app.get_config("clinic_phone", ""))
        self.txt_clinic_email.setText(self.app.get_config("clinic_email", ""))
        
        # Sécurité
        self.check_face.setChecked(self.app.get_config("face_auth_required", "0") == "1")
        self.check_mfa.setChecked(self.app.get_config("mfa_enabled", "0") == "1")
        self.check_audit.setChecked(self.app.get_config("blockchain_audit_forced", "1") == "1")
        self.check_auto_ia.setChecked(self.app.get_config("auto_predict_enabled", "1") == "1")
        
        # Maintenance & Backup
        self.check_maintenance.setChecked(self.app.get_config("maintenance_mode", "0") == "1")
        self.check_auto_backup.setChecked(self.app.get_config("auto_backup", "1") == "1")
        self.sb_backup_interval.setValue(int(self.app.get_config("backup_interval_hours", "24")))

    def _on_save_all(self):
        """Enregistre tous les paramètres en base."""
        try:
            settings = {
                "clinic_name": self.txt_clinic_name.text(),
                "clinic_address": self.txt_clinic_address.text(),
                "clinic_phone": self.txt_clinic_phone.text(),
                "clinic_email": self.txt_clinic_email.text(),
                "face_auth_required": "1" if self.check_face.isChecked() else "0",
                "mfa_enabled": "1" if self.check_mfa.isChecked() else "0",
                "blockchain_audit_forced": "1" if self.check_audit.isChecked() else "0",
                "auto_predict_enabled": "1" if self.check_auto_ia.isChecked() else "0",
                "maintenance_mode": "1" if self.check_maintenance.isChecked() else "0",
                "auto_backup": "1" if self.check_auto_backup.isChecked() else "0",
                "backup_interval_hours": str(self.sb_backup_interval.value())
            }
            
            for key, val in settings.items():
                self.app.set_config(key, val)
                
            QtWidgets.QMessageBox.information(self, "Succès", "Tous les paramètres ont été enregistrés avec succès.")
            
            # Logger l'action d'audit
            self.app.security.log_audit_event(
                self.app.current_user_id(),
                "UPDATE_SYSTEM_SETTINGS",
                "system_config",
                None,
                None,
                "All settings updated"
            )
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement : {e}")

    def _manual_backup(self):
        """Simule ou lance une sauvegarde de la base de données."""
        try:
            import shutil
            import datetime
            
            db_path = self.app.db.db_path
            backup_dir = "./db/backups"
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"medierp_backup_{timestamp}.db")
            
            shutil.copy2(db_path, backup_path)
            
            QtWidgets.QMessageBox.information(self, "Sauvegarde Réussie", f"La base de données a été sauvegardée :\n{backup_path}")
            
            self.app.security.log_audit_event(
                self.app.current_user_id(),
                "MANUAL_BACKUP",
                "database",
                None,
                None,
                f"Backup path: {backup_path}"
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erreur de Sauvegarde", f"Impossible de créer la sauvegarde : {e}")
import os
