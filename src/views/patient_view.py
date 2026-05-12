"""
MediERP — Patient List View (Code-only, sans .ui)
Tableau clair, spacieux, avec recherche en temps réel et actions RBAC.
"""

from ..utils.qt_compat import QtWidgets, QtCore, QtGui
from ..core.app import SmartMedicalApp
import os


class PatientListView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self._setup_ui()
        self.refresh_list()

    # ──────────────────────── UI ────────────────────────

    def _setup_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── En-tête bleu
        hdr = QtWidgets.QFrame()
        hdr.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "stop:0 #1890ff, stop:1 #0050b3);"
        )
        hdr.setFixedHeight(72)
        hdr_lay = QtWidgets.QHBoxLayout(hdr)
        hdr_lay.setContentsMargins(30, 0, 30, 0)

        lbl = QtWidgets.QLabel("👥 Mes Patients")
        lbl.setStyleSheet("font-size: 16pt; font-weight: 800; color: white;")
        hdr_lay.addWidget(lbl)
        hdr_lay.addStretch()

        self.lbl_count = QtWidgets.QLabel("")
        self.lbl_count.setStyleSheet(
            "background: rgba(255,255,255,0.2); color: white;"
            "border-radius: 12px; padding: 4px 14px; font-size: 10pt;"
        )
        hdr_lay.addWidget(self.lbl_count)
        root.addWidget(hdr)

        # ── Barre d'outils : recherche + bouton ajouter
        toolbar = QtWidgets.QWidget()
        toolbar.setStyleSheet("background: white; border-bottom: 1px solid #e8e8e8;")
        tb_lay = QtWidgets.QHBoxLayout(toolbar)
        tb_lay.setContentsMargins(24, 12, 24, 12)
        tb_lay.setSpacing(16)

        # Recherche
        search_frame = QtWidgets.QFrame()
        search_frame.setStyleSheet(
            "QFrame { background: #f8f9fb; border: 1px solid #d9d9d9;"
            "border-radius: 10px; padding: 2px 10px; }"
        )
        sf_lay = QtWidgets.QHBoxLayout(search_frame)
        sf_lay.setContentsMargins(8, 0, 8, 0)
        sf_lay.setSpacing(8)

        ic = QtWidgets.QLabel("🔍")
        ic.setStyleSheet("font-size: 13pt; background: transparent;")
        sf_lay.addWidget(ic)

        self.txtSearch = QtWidgets.QLineEdit()
        self.txtSearch.setPlaceholderText("Rechercher par nom ou prénom…")
        self.txtSearch.setStyleSheet(
            "QLineEdit { border: none; background: transparent; font-size: 12pt;"
            "color: #262626; }"
        )
        self.txtSearch.setMinimumHeight(40)
        self.txtSearch.textChanged.connect(self.refresh_list)
        sf_lay.addWidget(self.txtSearch)

        tb_lay.addWidget(search_frame, 1)
        tb_lay.addStretch()

        # Bouton Ajouter
        self.btnAdd = QtWidgets.QPushButton("➕  Nouveau patient")
        self.btnAdd.setObjectName("btnPrimary")
        self.btnAdd.setFixedHeight(44)
        self.btnAdd.setMinimumWidth(180)
        self.btnAdd.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btnAdd.clicked.connect(self._on_add_patient)
        tb_lay.addWidget(self.btnAdd)

        uid = self.app.current_user_id()
        can_add = (self.app.rbac.is_admin(uid) or
                   self.app.rbac.is_doctor(uid) or
                   self.app.rbac.is_secretary(uid))
        self.btnAdd.setVisible(can_add)

        root.addWidget(toolbar)

        # ── Tableau patients
        self.tablePatients = QtWidgets.QTableWidget()
        self.tablePatients.setColumnCount(6)
        self.tablePatients.setHorizontalHeaderLabels(
            ["ID", "Nom", "Prénom", "CIN", "Téléphone", "Actions"]
        )

        # Style général
        self.tablePatients.setAlternatingRowColors(True)
        self.tablePatients.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                font-size: 11pt;
                gridline-color: #f0f0f0;
                selection-background-color: #e6f7ff;
                selection-color: #0050b3;
                alternate-background-color: #fafafa;
            }
            QHeaderView::section {
                background-color: #f8f9fb;
                color: #595959;
                font-weight: 700;
                font-size: 10pt;
                border: none;
                border-bottom: 2px solid #e8e8e8;
                padding: 12px 16px;
            }
            QTableWidget::item {
                padding: 10px 14px;
            }
        """)
        self.tablePatients.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.tablePatients.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.tablePatients.setShowGrid(False)
        self.tablePatients.verticalHeader().setVisible(False)
        self.tablePatients.verticalHeader().setDefaultSectionSize(52)
        self.tablePatients.horizontalHeader().setStretchLastSection(True)

        # Largeurs colonnes
        self.tablePatients.setColumnWidth(0, 60)
        self.tablePatients.setColumnWidth(1, 160)
        self.tablePatients.setColumnWidth(2, 160)
        self.tablePatients.setColumnWidth(3, 140)
        self.tablePatients.setColumnWidth(4, 140)

        # Masquer la colonne ID
        self.tablePatients.setColumnHidden(0, True)

        self.tablePatients.cellDoubleClicked.connect(self._on_patient_double_clicked)

        root.addWidget(self.tablePatients)

    # ──────────────────────── DATA ────────────────────────

    def refresh_list(self):
        search = self.txtSearch.text().strip() if hasattr(self, 'txtSearch') else ""
        if search:
            query = (
                "SELECT * FROM patients "
                "WHERE (last_name LIKE ? OR first_name LIKE ?) "
                "AND is_active=1 ORDER BY last_name, first_name"
            )
            params = (f"%{search}%", f"%{search}%")
        else:
            query = "SELECT * FROM patients WHERE is_active=1 ORDER BY last_name, first_name"
            params = ()

        try:
            patients = self.app.db.fetch_all(query, params)
        except Exception as e:
            patients = []
            print(f"[PatientList] Erreur DB: {e}")

        self._populate_table(patients)

    def _populate_table(self, patients):
        uid = self.app.current_user_id()
        can_edit = (self.app.rbac.is_admin(uid) or
                    self.app.rbac.is_doctor(uid) or
                    self.app.rbac.is_secretary(uid))
        can_delete = self.app.rbac.is_admin(uid)

        self.tablePatients.setRowCount(0)
        for row, p in enumerate(patients):
            self.tablePatients.insertRow(row)

            # ID (caché)
            self.tablePatients.setItem(row, 0, QtWidgets.QTableWidgetItem(str(p['id'])))

            # Nom / Prénom
            for col, field in [(1, 'last_name'), (2, 'first_name')]:
                it = QtWidgets.QTableWidgetItem(p.get(field) or "—")
                it.setFont(QtGui.QFont("", -1, QtGui.QFont.Weight.Bold if col == 1 else QtGui.QFont.Weight.Normal))
                self.tablePatients.setItem(row, col, it)

            # CIN
            self.tablePatients.setItem(row, 3, QtWidgets.QTableWidgetItem(p.get('cin') or "—"))

            # Téléphone
            phone_it = QtWidgets.QTableWidgetItem(p.get('phone') or "—")
            phone_it.setForeground(QtGui.QBrush(QtGui.QColor("#1890ff")))
            self.tablePatients.setItem(row, 4, phone_it)

            # Actions
            actions = QtWidgets.QWidget()
            a_lay = QtWidgets.QHBoxLayout(actions)
            a_lay.setContentsMargins(8, 4, 8, 4)
            a_lay.setSpacing(8)

            if can_edit:
                btn_e = QtWidgets.QPushButton("✏️ Modifier")
                btn_e.setFixedHeight(32)
                btn_e.setObjectName("btnSecondary")
                btn_e.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
                btn_e.clicked.connect(lambda _, pid=p['id']: self._on_edit_patient(pid))
                a_lay.addWidget(btn_e)

            btn_d = QtWidgets.QPushButton("📁 Dossier")
            btn_d.setFixedHeight(32)
            btn_d.setObjectName("btnPrimary")
            btn_d.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            btn_d.clicked.connect(lambda _, pid=p['id']: self._open_dossier(pid))
            a_lay.addWidget(btn_d)

            if can_delete:
                btn_del = QtWidgets.QPushButton("🗑️")
                btn_del.setFixedHeight(32)
                btn_del.setFixedWidth(40)
                btn_del.setObjectName("btnDanger")
                btn_del.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
                btn_del.clicked.connect(lambda _, pid=p['id']: self._on_delete_patient(pid))
                a_lay.addWidget(btn_del)

            a_lay.addStretch()
            self.tablePatients.setCellWidget(row, 5, actions)

        # Compteur
        n = len(patients)
        if hasattr(self, 'lbl_count'):
            self.lbl_count.setText(f"{n} patient{'s' if n != 1 else ''}")

    # ──────────────────────── ACTIONS ────────────────────────

    def search(self, text: str):
        """Appelée par la barre de recherche globale."""
        self.txtSearch.setText(text)

    def _on_patient_double_clicked(self, row, _col):
        id_item = self.tablePatients.item(row, 0)
        if not id_item:
            return
        pid = int(id_item.text())
        uid = self.app.current_user_id()
        win = self.window()
        if self.app.rbac.is_doctor(uid):
            if hasattr(win, "open_consultation"):
                win.open_consultation(pid)
        else:
            self._open_dossier(pid)

    def _open_dossier(self, patient_id: int):
        win = self.window()
        if hasattr(win, "open_patient_dossier"):
            win.open_patient_dossier(patient_id)

    def _on_add_patient(self):
        dialog = AddPatientDialog(self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            new_id = self.app.db.insert("patients", data)
            if new_id:
                QtWidgets.QMessageBox.information(
                    self, "Succès",
                    f"Patient {data['first_name']} {data['last_name']} ajouté avec succès."
                )
                self.refresh_list()
            else:
                QtWidgets.QMessageBox.warning(self, "Erreur", "Impossible d'ajouter le patient.")

    def _on_edit_patient(self, patient_id: int):
        data = self.app.db.get_by_id("patients", patient_id)
        if not data:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Patient introuvable.")
            return
        dialog = AddPatientDialog(self, data)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            update = dialog.get_data()
            if self.app.db.update("patients", patient_id, update):
                # Notification si c'est une secrétaire qui modifie
                uid = self.app.current_user_id()
                if self.app.rbac.is_secretary(uid):
                    from ..services.email_service import email_service
                    email = update.get('email') or data.get('email')
                    if email:
                        import threading
                        subj = "Modification de votre dossier administratif"
                        body = (f"Bonjour {data['first_name']},\n\n"
                                f"Votre dossier a été mis à jour par le secrétariat de MediERP.\n"
                                f"Si vous n'êtes pas à l'origine de cette demande, veuillez nous contacter.\n\n"
                                f"Cordialement,\nL'équipe MediERP")
                        threading.Thread(target=email_service.send_email, args=(email, subj, body), daemon=True).start()
                
                QtWidgets.QMessageBox.information(self, "Succès", "Patient mis à jour.")
                self.refresh_list()

    def _on_delete_patient(self, patient_id: int):
        reply = QtWidgets.QMessageBox.question(
            self, "Confirmation",
            "Supprimer ce patient ?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            if self.app.db.delete("patients", patient_id, hard=False):
                self.refresh_list()


# ─────────────────────────────────────────────
#  Dialog Ajouter / Modifier patient
# ─────────────────────────────────────────────
class AddPatientDialog(QtWidgets.QDialog):
    """Formulaire complet d'ajout / modification d'un patient."""

    FIELDS = [
        ("Prénom *",       "first_name",    "Ex : Mohamed"),
        ("Nom *",          "last_name",     "Ex : Bouazizi"),
        ("CIN",            "cin",           "Ex : 12345678"),
        ("Date naissance", "date_of_birth", "AAAA-MM-JJ"),
        ("Sexe",           "sex",           "M / F"),
        ("Téléphone",      "phone",         "Ex : +216 22 000 000"),
        ("Email",          "email",         "patient@email.com"),
        ("Adresse",        "address",       ""),
        ("Ville",          "city",          ""),
        ("Groupe sanguin", "blood_type",    "A+, B-, O+…"),
        ("Poids (kg)",     "weight_kg",     "Ex : 70"),
        ("Taille (cm)",    "height_cm",     "Ex : 175"),
    ]

    def __init__(self, parent=None, patient_data: dict = None):
        super().__init__(parent)
        self._data = patient_data or {}
        self.setWindowTitle("Modifier le Patient" if patient_data else "Nouveau Patient")
        self.setMinimumSize(640, 620)
        self.resize(640, 680)
        self._inputs = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(20)

        # Titre
        is_edit = bool(self._data)
        title = QtWidgets.QLabel("✏️ Modifier le Patient" if is_edit else "➕ Nouveau Patient")
        title.setStyleSheet("font-size: 16pt; font-weight: 800; color: #0050b3;")
        layout.addWidget(title)

        # Scroll
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        inner = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout(inner)
        form.setSpacing(14)
        form.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        for label, field, placeholder in self.FIELDS:
            inp = QtWidgets.QLineEdit()
            inp.setPlaceholderText(placeholder)
            inp.setMinimumHeight(40)
            inp.setText(str(self._data.get(field, '') or ''))
            form.addRow(f"  {label} :", inp)
            self._inputs[field] = inp

        scroll.setWidget(inner)
        layout.addWidget(scroll, 1)

        # Boutons
        btn_row = QtWidgets.QHBoxLayout()
        btn_cancel = QtWidgets.QPushButton("Annuler")
        btn_cancel.setFixedHeight(42)
        btn_cancel.clicked.connect(self.reject)
        btn_save = QtWidgets.QPushButton("Mettre à jour" if is_edit else "Enregistrer")
        btn_save.setObjectName("btnPrimary")
        btn_save.setFixedHeight(42)
        btn_save.clicked.connect(self._on_accept)
        btn_row.addWidget(btn_cancel)
        btn_row.addStretch()
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

    def _on_accept(self):
        if not self._inputs['first_name'].text().strip():
            QtWidgets.QMessageBox.warning(self, "Champ requis", "Le prénom est obligatoire.")
            return
        if not self._inputs['last_name'].text().strip():
            QtWidgets.QMessageBox.warning(self, "Champ requis", "Le nom est obligatoire.")
            return
        self.accept()

    def get_data(self) -> dict:
        d = {"is_active": 1}
        for field, inp in self._inputs.items():
            val = inp.text().strip()
            if val:
                if field in ('weight_kg', 'height_cm'):
                    try:
                        d[field] = float(val)
                    except ValueError:
                        pass
                else:
                    d[field] = val
        return d
