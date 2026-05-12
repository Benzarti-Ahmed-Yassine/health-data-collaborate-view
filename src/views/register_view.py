"""
Smart Medical AI - Registration View
Interface d'inscription pour le personnel médical
"""

from ..utils.qt_compat import QtWidgets, QtCore, QtGui
from ..core.security import SecurityManager

class RegisterDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.security = SecurityManager()
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Inscription Staff - MediERP")
        self.setMinimumSize(650, 900)
        self.resize(650, 900)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        # Main Container
        self.container = QtWidgets.QFrame(self)
        self.container.setObjectName("MainContainer")
        self.container.setGeometry(25, 25, 600, 850)

        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QtGui.QColor(67, 67, 67, 30))
        self.container.setGraphicsEffect(shadow)

        layout = QtWidgets.QVBoxLayout(self.container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)

        # Header
        ico = QtWidgets.QLabel("📝")
        ico.setObjectName("login_icon")
        ico.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(ico)

        title = QtWidgets.QLabel("Nouvelle Inscription")
        title.setObjectName("login_title")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QtWidgets.QLabel("Créez votre accès MediERP professionnel")
        subtitle.setObjectName("login_subtitle")
        subtitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        # Fields
        self.txtName = QtWidgets.QLineEdit()
        self.txtName.setPlaceholderText("Nom complet (ex: Dr. Ahmed Yassine)")
        layout.addWidget(self.txtName)

        self.txtEmail = QtWidgets.QLineEdit()
        self.txtEmail.setPlaceholderText("Email professionnel (@medierp.ai)")
        layout.addWidget(self.txtEmail)

        self.txtPassword = QtWidgets.QLineEdit()
        self.txtPassword.setPlaceholderText("Mot de passe sécurisé")
        self.txtPassword.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.txtPassword.textChanged.connect(self._validate_fields)
        layout.addWidget(self.txtPassword)

        # Password Criteria Label
        self.lblPasswordCriteria = QtWidgets.QLabel("Critère : 14 caractères minimum")
        self.lblPasswordCriteria.setProperty("class", "warning_text")
        self.lblPasswordCriteria.setStyleSheet("font-size: 9pt; font-style: italic;")
        layout.addWidget(self.lblPasswordCriteria)

        # Role Selection
        layout.addWidget(QtWidgets.QLabel("Sélectionnez votre rôle :"))
        self.cmbRole = QtWidgets.QComboBox()
        self.cmbRole.addItems(["DOCTOR", "SECRETARY", "ASSISTANT"])
        self.cmbRole.currentTextChanged.connect(self._on_role_changed)
        layout.addWidget(self.cmbRole)

        # Extra Fields (Doctor)
        self.doctor_group = QtWidgets.QWidget()
        doc_layout = QtWidgets.QVBoxLayout(self.doctor_group)
        doc_layout.setContentsMargins(0, 0, 0, 0)
        
        self.txtRPPS = QtWidgets.QLineEdit()
        self.txtRPPS.setPlaceholderText("Numéro RPPS (11 chiffres)")
        doc_layout.addWidget(self.txtRPPS)
        
        self.txtSpecialty = QtWidgets.QLineEdit()
        self.txtSpecialty.setPlaceholderText("Spécialité Médicale")
        doc_layout.addWidget(self.txtSpecialty)
        
        layout.addWidget(self.doctor_group)

        # Status
        self.lblStatus = QtWidgets.QLabel("")
        self.lblStatus.setObjectName("login_status")
        self.lblStatus.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lblStatus)

        # Action Buttons
        self.btnRegister = QtWidgets.QPushButton("Créer mon compte 🚀")
        self.btnRegister.setObjectName("btnPrimary")
        self.btnRegister.setFixedHeight(56)
        self.btnRegister.clicked.connect(self._on_register)
        layout.addWidget(self.btnRegister)

        btn_cancel = QtWidgets.QPushButton("Annuler")
        btn_cancel.setObjectName("btnSecondary")
        btn_cancel.setFixedHeight(45)
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_cancel)

    def _on_role_changed(self, role):
        self.doctor_group.setVisible(role == "DOCTOR")
        
        # Mettre à jour les critères
        min_pass = self.security.ROLE_CONFIG.get(role, {"min_pass": 14})["min_pass"]
        self.lblPasswordCriteria.setText(f"🔒 Critère de sécurité : {min_pass} caractères minimum")

    def _validate_fields(self):
        """Validation visuelle en temps réel"""
        role = self.cmbRole.currentText()
        min_pass = self.security.ROLE_CONFIG.get(role, {"min_pass": 14})["min_pass"]
        pwd = self.txtPassword.text()
        
        if len(pwd) >= min_pass:
            self.lblPasswordCriteria.setProperty("class", "success_text")
            self.lblPasswordCriteria.style().unpolish(self.lblPasswordCriteria)
            self.lblPasswordCriteria.style().polish(self.lblPasswordCriteria)
            self.lblPasswordCriteria.setText(f"✅ Mot de passe conforme ({len(pwd)} car.)")
        else:
            self.lblPasswordCriteria.setProperty("class", "warning_text")
            self.lblPasswordCriteria.style().unpolish(self.lblPasswordCriteria)
            self.lblPasswordCriteria.style().polish(self.lblPasswordCriteria)
            self.lblPasswordCriteria.setText(f"🔒 Critère de sécurité : {min_pass} caractères minimum")

    def _on_register(self):
        data = {
            "full_name": self.txtName.text().strip(),
            "email": self.txtEmail.text().strip(),
            "password": self.txtPassword.text().strip(),
            "role": self.cmbRole.currentText(),
            "rpps_number": self.txtRPPS.text().strip() if self.cmbRole.currentText() == "DOCTOR" else None,
            "specialty": self.txtSpecialty.text().strip() if self.cmbRole.currentText() == "DOCTOR" else None
        }

        # Validation basique
        if not data["full_name"] or not data["email"] or not data["password"]:
            self.lblStatus.setText("❌ Champs obligatoires manquants")
            self.lblStatus.setProperty("class", "danger")
            self.lblStatus.style().unpolish(self.lblStatus)
            self.lblStatus.style().polish(self.lblStatus)
            return

        if "@" not in data["email"]:
            self.lblStatus.setText("❌ Format email invalide")
            self.lblStatus.setProperty("class", "danger")
            self.lblStatus.style().unpolish(self.lblStatus)
            self.lblStatus.style().polish(self.lblStatus)
            return

        try:
            if self.security.register_user(data):
                QtWidgets.QMessageBox.information(self, "Succès", "Compte créé ! Vous pouvez maintenant vous connecter.")
                self.accept()
            else:
                self.lblStatus.setText("❌ Cet email est déjà utilisé")
                self.lblStatus.setStyleSheet("color: #ff4d4f;")
        except Exception as e:
            self.lblStatus.setText(f"❌ Erreur: {str(e)}")
            self.lblStatus.setStyleSheet("color: #ff4d4f;")
