"""
Smart Medical AI - Professional Login (Senior Developer Edition)
Design & Logique alignés sur MediERP
"""

import os
from ..utils.qt_compat import QtWidgets, QtCore, QtGui, uic
from ..core.security import SecurityManager

class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connexion - MediERP")
        self.setMinimumSize(600, 850)
        self.resize(600, 850)
        
        self.setObjectName("login_dialog")
        
        self.security = SecurityManager()
        self.user_data = None
        self._setup_ui()

    def _setup_ui(self):
        # Master Layout
        master_layout = QtWidgets.QVBoxLayout(self)
        master_layout.setContentsMargins(80, 60, 80, 60)

        # Application du fond clair et carte blanche via le ThemeManager
        self.setProperty("class", "login_view")

        # Main Card (White Container)
        self.container = QtWidgets.QFrame()
        self.container.setObjectName("MainContainer")
        master_layout.addWidget(self.container)

        # Drop Shadow
        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 5)
        shadow.setColor(QtGui.QColor(0, 0, 0, 80))
        self.container.setGraphicsEffect(shadow)

        layout = QtWidgets.QVBoxLayout(self.container)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(20)

        # 1. Logo & Titre
        lbl_icon = QtWidgets.QLabel("➕")
        lbl_icon.setObjectName("login_icon")
        lbl_icon.setStyleSheet("color: #722ed1; font-size: 65pt; font-weight: bold;")
        lbl_icon.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_icon)

        lbl_title = QtWidgets.QLabel("MediERP")
        lbl_title.setObjectName("login_title")
        lbl_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)

        lbl_subtitle = QtWidgets.QLabel("Système de gestion médicale")
        lbl_subtitle.setObjectName("login_subtitle")
        lbl_subtitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_subtitle)
        
        layout.addSpacing(10)

        # 2. Champs Saisie
        self.txtEmail = QtWidgets.QLineEdit()
        self.txtEmail.setPlaceholderText("✉  Email professionnel")
        self.txtEmail.setFixedHeight(50)
        self.txtEmail.setStyleSheet("background-color: #ffffff; border: 1px solid #e1e4e8; border-radius: 8px; padding-left: 15px; color: #0050b3; font-size: 11pt;")
        layout.addWidget(self.txtEmail)
        
        # Champ Mot de passe
        self.txtPassword = QtWidgets.QLineEdit()
        self.txtPassword.setPlaceholderText("🔒  Mot de passe")
        self.txtPassword.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.txtPassword.setFixedHeight(50)
        self.txtPassword.setStyleSheet("background-color: #ffffff; border: 1px solid #e1e4e8; border-radius: 8px; padding-left: 15px; color: #0050b3; font-size: 11pt;")
        layout.addWidget(self.txtPassword)

        # 3. Boutons
        layout.addSpacing(10)
        self.btnLogin = QtWidgets.QPushButton("🚀 Se connecter")
        self.btnLogin.setObjectName("btnPrimary")
        self.btnLogin.setFixedHeight(50)
        self.btnLogin.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btnLogin.setStyleSheet("background-color: #1890ff; color: white; font-weight: bold; font-size: 11pt; border-radius: 8px;")
        self.btnLogin.clicked.connect(self._on_login)
        layout.addWidget(self.btnLogin)

        self.btnFaceID = QtWidgets.QPushButton("📷 Face ID")
        self.btnFaceID.setObjectName("btnSecondary")
        self.btnFaceID.setFixedHeight(50)
        self.btnFaceID.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btnFaceID.setStyleSheet("background-color: #e6f7ff; color: #1890ff; border: 1px solid #1890ff; font-weight: bold; font-size: 11pt; border-radius: 8px;")
        self.btnFaceID.clicked.connect(self._on_face_id)
        layout.addWidget(self.btnFaceID)

        # 4. Status Error Message
        self.lblStatus = QtWidgets.QLabel("")
        self.lblStatus.setObjectName("login_status")
        self.lblStatus.setStyleSheet("color: #ff4d4f; font-weight: 500; font-size: 10pt;")
        self.lblStatus.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lblStatus)

        layout.addStretch()

        # 5. Liens supplémentaires
        links_layout = QtWidgets.QHBoxLayout()
        
        self.btnPatientSpace = QtWidgets.QPushButton("Espace Patient")
        self.btnPatientSpace.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btnPatientSpace.setStyleSheet("background-color: transparent; color: #1890ff; font-weight: bold; border: none; font-size: 10pt; text-decoration: none;")
        self.btnPatientSpace.clicked.connect(self._on_switch_to_patient)
        
        self.btnRegisterLink = QtWidgets.QPushButton("S'inscrire")
        self.btnRegisterLink.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btnRegisterLink.setStyleSheet("background-color: transparent; color: #8c8c8c; border: none; font-size: 10pt; text-decoration: underline;")
        self.btnRegisterLink.clicked.connect(self._on_open_register)

        links_layout.addWidget(self.btnPatientSpace)
        links_layout.addStretch()
        links_layout.addWidget(self.btnRegisterLink)

        layout.addLayout(links_layout)

    def _on_login(self):
        email = self.txtEmail.text().strip()
        password = self.txtPassword.text().strip()
        
        try:
            result = self.security.authenticate(email, password)
            if result:
                self.user_data = result
                self.accept()
            else:
                self.lblStatus.setText("❌ Identifiants incorrects")
        except PermissionError as pe:
            self.lblStatus.setText(f"🛑 {str(pe)}")
        except Exception as e:
            self.lblStatus.setText(f"❌ Erreur: {str(e)}")
        
        self.lblStatus.setProperty("class", "danger")
        self.lblStatus.style().unpolish(self.lblStatus)
        self.lblStatus.style().polish(self.lblStatus)

    def _on_open_register(self):
        """Ouvre l'interface de création de compte."""
        from .register_view import RegisterDialog
        self.hide()
        reg = RegisterDialog(self.parent()) # Use parent to avoid centering on hidden window
        reg.exec()
        self.show()

    def _on_face_id(self):
        """Ouvre l'interface de reconnaissance faciale avec détection automatique."""
        from .biometric_widget import BiometricWidget

        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Authentification Biométrique")
        dialog.setMinimumSize(600, 650)
        dialog.resize(600, 650)
        dialog.setStyleSheet("background-color: white;")

        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        lbl_guide = QtWidgets.QLabel("Regardez la caméra — la reconnaissance se fait automatiquement.")
        lbl_guide.setProperty("class", "secondary_text")
        lbl_guide.setWordWrap(True)
        layout.addWidget(lbl_guide)

        bio_widget = BiometricWidget(dialog)
        layout.addWidget(bio_widget)

        # Manual fallback button
        btn_verify = QtWidgets.QPushButton("Vérifier maintenant")
        btn_verify.setFixedHeight(45)
        btn_verify.setObjectName("btnPrimary")
        btn_verify.clicked.connect(bio_widget.try_authenticate)
        layout.addWidget(btn_verify)

        btn_cancel = QtWidgets.QPushButton("Annuler")
        btn_cancel.setFixedHeight(38)
        btn_cancel.clicked.connect(dialog.reject)
        layout.addWidget(btn_cancel)

        # Connexion des signaux
        def on_auth_success(user_id):
            user = self.security.db.fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))
            if user:
                self.user_data = dict(user)
                bio_widget.stop_camera()
                dialog.accept()
                self.accept()
            else:
                QtWidgets.QMessageBox.warning(dialog, "Erreur", "Utilisateur non trouvé dans la base.")

        bio_widget.auth_success.connect(on_auth_success)

        if bio_widget.start_camera():
            # Auto-start continuous authentication
            bio_widget.start_authentication()
            dialog.exec()
            bio_widget.stop_camera()
        else:
            QtWidgets.QMessageBox.critical(self, "Erreur", "Impossible d'accéder à la caméra.")

    def _on_switch_to_patient(self):
        self.hide()
        dlg = PatientLoginDialog(self.parent())
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.user_data = dlg.get_user()
            self.accept()
        else:
            self.show()

    def get_user(self) -> dict:
        return self.user_data or {}

class PatientLoginDialog(QtWidgets.QDialog):
    """Espace Patient - Design MediERP"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Espace Patient - MediERP")
        self.setMinimumSize(500, 600)
        self.resize(500, 600)
        self.security = SecurityManager()
        self.user_data = None
        self._setup_ui()

    def _setup_ui(self):
        # Master Layout
        master_layout = QtWidgets.QVBoxLayout(self)
        master_layout.setContentsMargins(80, 60, 80, 60)

        self.setProperty("class", "login_view")

        self.container = QtWidgets.QFrame(self)
        self.container.setObjectName("MainContainer")
        master_layout.addWidget(self.container)
        
        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 5)
        shadow.setColor(QtGui.QColor(0, 0, 0, 80))
        self.container.setGraphicsEffect(shadow)
        
        layout = QtWidgets.QVBoxLayout(self.container)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(20)
        
        lbl_icon = QtWidgets.QLabel("👨‍⚕️")
        lbl_icon.setObjectName("login_icon")
        lbl_icon.setStyleSheet("color: #52c41a; font-size: 65pt; font-weight: bold;")
        lbl_icon.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_icon)

        lbl_title = QtWidgets.QLabel("Espace Patient")
        lbl_title.setObjectName("login_title")
        lbl_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)
        
        lbl_subtitle = QtWidgets.QLabel("Consultez votre dossier médical")
        lbl_subtitle.setObjectName("login_subtitle")
        lbl_subtitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_subtitle)
        
        layout.addSpacing(10)
        
        self.txtCin = QtWidgets.QLineEdit()
        self.txtCin.setPlaceholderText("💳  Votre CIN (ex: AB123456)")
        self.txtCin.setFixedHeight(50)
        self.txtCin.setStyleSheet("background-color: #ffffff; border: 1px solid #e1e4e8; border-radius: 8px; padding-left: 15px; color: #0050b3; font-size: 11pt;")
        layout.addWidget(self.txtCin)
        
        layout.addSpacing(10)
        self.btnConnect = QtWidgets.QPushButton("🚀 Accéder")
        self.btnConnect.setFixedHeight(50)
        self.btnConnect.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btnConnect.setStyleSheet("background-color: #52c41a; color: white; font-weight: bold; font-size: 11pt; border-radius: 8px;")
        self.btnConnect.clicked.connect(self._on_login)
        layout.addWidget(self.btnConnect)
        
        self.lblStatus = QtWidgets.QLabel("")
        self.lblStatus.setStyleSheet("color: #ff4d4f; font-weight: 500; font-size: 10pt;")
        self.lblStatus.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lblStatus)
        
        layout.addStretch()
        
        btn_close = QtWidgets.QPushButton("Retour au Staff")
        btn_close.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("background-color: transparent; color: #8c8c8c; border: none; font-size: 10pt; text-decoration: underline;")
        btn_close.clicked.connect(self.reject)
        layout.addWidget(btn_close)

    def _on_login(self):
        cin = self.txtCin.text().strip().upper()
        if not cin:
            self.lblStatus.setText("❌ Veuillez saisir votre CIN")
            self.lblStatus.setProperty("class", "danger")
            self.lblStatus.style().unpolish(self.lblStatus)
            self.lblStatus.style().polish(self.lblStatus)
            return
            
        result = self.security.authenticate_patient(cin)
        if result:
            self.user_data = result
            self.accept()
        else:
            self.lblStatus.setText("❌ CIN non reconnu")
            self.lblStatus.setProperty("class", "danger")
            self.lblStatus.style().unpolish(self.lblStatus)
            self.lblStatus.style().polish(self.lblStatus)

    def get_user(self) -> dict:
        return self.user_data or {}
