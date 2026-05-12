"""
MediERP — User Management View (Admin)
Gestion complète des utilisateurs avec modification de rôle et statut.
"""

from ...utils.qt_compat import QtWidgets, QtCore, QtGui
from ...core.app import SmartMedicalApp


class UserManagementView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self._all_users = []
        self._setup_ui()
        self._load_users()

    # ================================================================
    # UI SETUP
    # ================================================================

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header_layout = QtWidgets.QHBoxLayout()
        header_title = QtWidgets.QLabel("👥 Gestion des Utilisateurs")
        header_title.setObjectName("header_title")
        header_layout.addWidget(header_title)
        header_layout.addStretch()

        self.btn_add = QtWidgets.QPushButton("➕ Ajouter un utilisateur")
        self.btn_add.setFixedHeight(40)
        self.btn_add.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        # Use primary themed button style
        self.btn_add.setObjectName("btnPrimary")
        self.btn_add.clicked.connect(self._on_add_user)
        header_layout.addWidget(self.btn_add)
        layout.addLayout(header_layout)

        # Barre de recherche
        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Rechercher par nom, email ou rôle...")
        self.search_bar.setFixedHeight(45)
        self.search_bar.setObjectName("search_bar")
        self.search_bar.textChanged.connect(self._filter_users)
        layout.addWidget(self.search_bar)

        # Table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Nom complet", "Email", "Rôle", "Statut", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 160)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setObjectName("user_table")
        layout.addWidget(self.table)

    # ================================================================
    # DATA
    # ================================================================

    def _load_users(self):
        try:
            self._all_users = self.app.db.fetch_all(
                "SELECT id, full_name, email, role, is_active FROM users ORDER BY id DESC"
            )
            self._render_table(self._all_users)
        except Exception as e:
            print(f"[UserMgmt] Erreur chargement utilisateurs: {e}")

    def _render_table(self, users: list):
        self.table.setRowCount(0)
        role_colors = {
            "ADMIN":     "#722ed1",
            "DOCTOR":    "#1890ff",
            "SECRETARY": "#13c2c2",
            "ASSISTANT": "#52c41a",
            "PATIENT":   "#fa8c16",
        }

        for i, user in enumerate(users):
            self.table.insertRow(i)
            row_height = 48
            self.table.setRowHeight(i, row_height)

            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(user['id'])))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(user['full_name'] or "N/A"))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(user['email']))

            # Badge de rôle
            role = user['role'] or "INCONNU"
            color = role_colors.get(role, "#434343")
            role_lbl = QtWidgets.QLabel(f"  {role}  ")
            role_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            # Keep role badge colored to indicate role; text remains readable on light theme
            role_lbl.setStyleSheet(
                f"color: {color}; font-weight: bold; font-size: 9pt; "
                f"background-color: {color}20; border-radius: 6px; padding: 3px 8px;"
            )
            self.table.setCellWidget(i, 3, role_lbl)

            # Statut
            is_active = bool(user['is_active'])
            status_lbl = QtWidgets.QLabel("Actif" if is_active else "Inactif")
            status_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            status_lbl.setStyleSheet(
                f"color: {'#52c41a' if is_active else '#ff4d4f'}; font-weight: 600; font-size: 9pt;"
            )
            self.table.setCellWidget(i, 4, status_lbl)

            # Actions
            actions_widget = QtWidgets.QWidget()
            al = QtWidgets.QHBoxLayout(actions_widget)
            al.setContentsMargins(4, 4, 4, 4)
            al.setSpacing(6)

            btn_edit = QtWidgets.QPushButton("✏️ Modifier")
            btn_edit.setFixedHeight(32)
            btn_edit.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            # Use default themed button (no inline color) for consistency
            btn_edit.clicked.connect(lambda checked, u=user: self._on_edit_user(u))

            btn_toggle = QtWidgets.QPushButton("🔴" if is_active else "🟢")
            btn_toggle.setFixedSize(32, 32)
            btn_toggle.setToolTip("Désactiver" if is_active else "Activer")
            btn_toggle.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            # Keep toggle colored to indicate status; minimal inline styling retained
            btn_toggle.setStyleSheet(
                "background-color: #fff1f0; border: 1px solid #ffccc7; border-radius: 6px; font-size: 11pt;"
                if is_active else
                "background-color: #f6ffed; border: 1px solid #b7eb8f; border-radius: 6px; font-size: 11pt;"
            )
            btn_toggle.clicked.connect(lambda checked, uid=user['id'], act=is_active: self._on_toggle_status(uid, act))

            al.addWidget(btn_edit)
            al.addWidget(btn_toggle)
            self.table.setCellWidget(i, 5, actions_widget)

    def _filter_users(self, text: str):
        filtered = [
            u for u in self._all_users
            if text.lower() in (u['full_name'] or "").lower()
            or text.lower() in (u['email'] or "").lower()
            or text.lower() in (u['role'] or "").lower()
        ]
        self._render_table(filtered)

    # ================================================================
    # ACTIONS
    # ================================================================

    def _on_add_user(self):
        from ..register_view import RegisterDialog
        dialog = RegisterDialog(self)
        dialog.exec()
        self._load_users()

    def _on_edit_user(self, user: dict):
        dialog = _EditUserDialog(user, self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if self.app.db.update("users", user['id'], data):
                # Synchroniser le rôle RBAC
                if 'role' in data:
                    self.app.rbac.change_role(user['id'], data['role'])
                QtWidgets.QMessageBox.information(self, "Succès", "Utilisateur mis à jour.")
                QtCore.QTimer.singleShot(0, self._load_users)
            else:
                QtWidgets.QMessageBox.critical(self, "Erreur", "Impossible de mettre à jour l'utilisateur.")

    def _on_toggle_status(self, user_id: int, is_active: bool):
        action = "désactiver" if is_active else "réactiver"
        reply = QtWidgets.QMessageBox.question(
            self, "Confirmation", f"Voulez-vous {action} cet utilisateur ?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            new_status = 0 if is_active else 1
            if self.app.db.update("users", user_id, {"is_active": new_status}):
                QtCore.QTimer.singleShot(0, self._load_users)


# ================================================================
# Dialog d'édition utilisateur
# ================================================================

class _EditUserDialog(QtWidgets.QDialog):
    """Dialog de modification du rôle et du statut d'un utilisateur."""

    ROLES = ["ADMIN", "DOCTOR", "SECRETARY", "ASSISTANT", "PATIENT"]

    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle(f"Modifier — {user.get('full_name', 'Utilisateur')}")
        self.setMinimumSize(550, 650)
        self.resize(550, 650)
        self.setObjectName("dialog_white")
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        # Titre
        lbl = QtWidgets.QLabel(f"<b>Modifier l'utilisateur</b>")
        lbl.setObjectName("dialog_title")
        layout.addWidget(lbl)

        lbl_email = QtWidgets.QLabel(f"Email : {self.user.get('email', '')}")
        lbl_email.setObjectName("dialog_subtitle")
        layout.addWidget(lbl_email)

        form = QtWidgets.QFormLayout()
        form.setSpacing(12)

        # Nom complet
        self.txt_name = QtWidgets.QLineEdit(self.user.get('full_name') or "")
        self.txt_name.setFixedHeight(38)
        self.txt_name.setObjectName("dlg_input")
        form.addRow("Nom complet :", self.txt_name)

        # Rôle
        self.cb_role = QtWidgets.QComboBox()
        self.cb_role.addItems(self.ROLES)
        current_role = self.user.get('role', 'DOCTOR')
        idx = self.cb_role.findText(current_role)
        if idx >= 0:
            self.cb_role.setCurrentIndex(idx)
        self.cb_role.setFixedHeight(38)
        self.cb_role.setObjectName("dlg_input")
        form.addRow("Rôle :", self.cb_role)

        # Statut
        self.chk_active = QtWidgets.QCheckBox("Compte actif")
        self.chk_active.setChecked(bool(self.user.get('is_active', 1)))
        form.addRow("Statut :", self.chk_active)

        # Add form FIRST, then biometrics below
        layout.addLayout(form)

        # ── Separator
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        line.setObjectName("divider_line")
        layout.addWidget(line)

        # ── Biometric section
        bio_layout = QtWidgets.QHBoxLayout()
        self.lbl_bio_status = QtWidgets.QLabel("Biométrie : Non configurée")
        self.lbl_bio_status.setObjectName("bio_status")

        # Check if already enrolled
        try:
            from ...services.biometric_service import biometric_service
            if self.user['id'] in biometric_service._encodings:
                self.lbl_bio_status.setText("Biométrie : ✅ Configurée")
                self.lbl_bio_status.setStyleSheet("color: #52c41a; font-size: 9pt; font-weight: bold;")
        except Exception:
            pass

        self.btn_enroll = QtWidgets.QPushButton("📷 Enrôler Visage")
        self.btn_enroll.setObjectName("btnEnroll")
        self.btn_enroll.clicked.connect(self._on_enroll_face)

        bio_layout.addWidget(self.lbl_bio_status)
        bio_layout.addStretch()
        bio_layout.addWidget(self.btn_enroll)
        layout.addLayout(bio_layout)
        layout.addStretch()

        btns = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Save |
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_data(self) -> dict:
        return {
            "full_name": self.txt_name.text().strip(),
            "role": self.cb_role.currentText(),
            "is_active": 1 if self.chk_active.isChecked() else 0,
        }

    def _on_enroll_face(self):
        """Lance la capture biométrique pour cet utilisateur."""
        from ..biometric_widget import BiometricWidget
        
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(f"Enrôlement - {self.user['full_name']}")
        dialog.setMinimumSize(600, 650)
        dialog.resize(600, 650)
        dialog.setObjectName("dialog_white")
        
        vbox = QtWidgets.QVBoxLayout(dialog)
        
        # Guide
        guide = QtWidgets.QLabel("Regardez fixement la caméra pendant la capture (5 échantillons).")
        guide.setObjectName("dialog_guide")
        guide.setWordWrap(True)
        vbox.addWidget(guide)
        
        bio_widget = BiometricWidget(dialog)
        vbox.addWidget(bio_widget)
        
        # Action buttons
        bbox = QtWidgets.QHBoxLayout()
        btn_start = QtWidgets.QPushButton("🚀 Commencer")
        btn_start.setFixedHeight(40)
        btn_start.setObjectName("btnSuccess")
        
        btn_cancel = QtWidgets.QPushButton("Annuler")
        btn_cancel.setFixedHeight(40)
        
        bbox.addWidget(btn_start)
        bbox.addWidget(btn_cancel)
        vbox.addLayout(bbox)
        
        # Logic
        def start_capture():
            btn_start.setEnabled(False)
            bio_widget.start_enrollment(self.user['id'])
            
        def on_complete(success):
            if success:
                self.lbl_bio_status.setText("Biométrie : ✅ Configurée")
                self.lbl_bio_status.setStyleSheet("color: #52c41a; font-size: 9pt; font-weight: bold;")
                QtWidgets.QMessageBox.information(dialog, "Succès", "Visage enrôlé avec succès !")
                dialog.accept()
                
        btn_start.clicked.connect(start_capture)
        btn_cancel.clicked.connect(dialog.reject)
        bio_widget.enrollment_complete.connect(on_complete)
        
        if bio_widget.start_camera():
            dialog.exec()
            bio_widget.stop_camera()
        else:
            QtWidgets.QMessageBox.critical(self, "Erreur", "Impossible d'accéder à la caméra.")
