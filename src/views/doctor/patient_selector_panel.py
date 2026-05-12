"""
MediERP — Patient Selector Panel
Panneau de sélection patient à injecter dans la vue consultation.
"""

from ...utils.qt_compat import QtWidgets, QtCore, QtGui
from ...core.app import SmartMedicalApp


class PatientSelectorPanel(QtWidgets.QFrame):
    """
    Barre de sélection patient à placer en haut de la vue consultation.
    Emet patient_selected(patient_id) quand un patient est choisi.
    """
    patient_selected = QtCore.Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self._patients = []
        self._current_id = None
        self._setup_ui()
        self._load_patients()

    def _setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background: white;
                border-bottom: 2px solid #e8e8e8;
            }
        """)
        self.setFixedHeight(70)

        row = QtWidgets.QHBoxLayout(self)
        row.setContentsMargins(20, 10, 20, 10)
        row.setSpacing(16)

        # Icône et label
        lbl = QtWidgets.QLabel("🔎 Patient :")
        lbl.setStyleSheet("font-size: 12pt; font-weight: 700; color: #0050b3;")
        row.addWidget(lbl)

        # Champ de recherche avec auto-complétion
        self.txt_search = QtWidgets.QLineEdit()
        self.txt_search.setPlaceholderText("Taper le nom, prénom ou CIN du patient…")
        self.txt_search.setMinimumHeight(44)
        self.txt_search.setMinimumWidth(320)
        self.txt_search.setStyleSheet("""
            QLineEdit {
                border: 2px solid #d9d9d9; border-radius: 10px;
                padding: 0 14px; font-size: 12pt; color: #262626;
                background: #f8f9fb;
            }
            QLineEdit:focus { border-color: #1890ff; background: white; }
        """)
        self.txt_search.textChanged.connect(self._on_search)
        row.addWidget(self.txt_search)

        # ComboBox liste filtrée
        self.cb_patient = QtWidgets.QComboBox()
        self.cb_patient.setMinimumHeight(44)
        self.cb_patient.setMinimumWidth(280)
        self.cb_patient.setStyleSheet("""
            QComboBox {
                border: 2px solid #d9d9d9; border-radius: 10px;
                padding: 0 14px; font-size: 11pt; color: #262626;
                background: white;
            }
            QComboBox:focus { border-color: #1890ff; }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox QAbstractItemView {
                border: 1px solid #d9d9d9; font-size: 11pt;
                selection-background-color: #e6f7ff;
            }
        """)
        self.cb_patient.currentIndexChanged.connect(self._on_combo_changed)
        row.addWidget(self.cb_patient)

        # Bouton Charger
        self.btn_load = QtWidgets.QPushButton("📂 Charger")
        self.btn_load.setFixedHeight(44)
        self.btn_load.setMinimumWidth(120)
        self.btn_load.setObjectName("btnPrimary")
        self.btn_load.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btn_load.clicked.connect(self._on_load)
        row.addWidget(self.btn_load)

        # Badge patient actif
        self.lbl_active = QtWidgets.QLabel("")
        self.lbl_active.setStyleSheet(
            "background: #f6ffed; color: #52c41a; border: 1px solid #b7eb8f;"
            "border-radius: 12px; padding: 4px 14px; font-size: 10pt; font-weight: bold;"
        )
        self.lbl_active.hide()
        row.addWidget(self.lbl_active)

        row.addStretch()

    def _load_patients(self):
        try:
            self._patients = self.app.db.fetch_all(
                "SELECT id, first_name, last_name, cin FROM patients WHERE is_active=1 ORDER BY last_name, first_name"
            )
            self._fill_combo(self._patients)
        except Exception as e:
            print(f"[PatientSelector] Erreur: {e}")

    def _fill_combo(self, patients):
        self.cb_patient.blockSignals(True)
        self.cb_patient.clear()
        self.cb_patient.addItem("— Sélectionner un patient —", None)
        for p in patients:
            label = f"{p['last_name']} {p['first_name']}"
            self.cb_patient.addItem(label, p['id'])
        self.cb_patient.blockSignals(False)

    def _on_search(self, text):
        text = text.strip().lower()
        if text:
            filtered = [
                p for p in self._patients
                if text in (p['last_name'] or '').lower()
                or text in (p['first_name'] or '').lower()
            ]
        else:
            filtered = self._patients
        self._fill_combo(filtered)

    def _on_combo_changed(self, idx):
        self._current_id = self.cb_patient.itemData(idx)

    def _on_load(self):
        pid = self._current_id
        if not pid:
            QtWidgets.QMessageBox.warning(
                self, "Aucun patient",
                "Veuillez sélectionner un patient dans la liste avant de charger."
            )
            return
        # Afficher badge
        pat = next((p for p in self._patients if p['id'] == pid), None)
        if pat:
            self.lbl_active.setText(f"✅ {pat['first_name']} {pat['last_name']}")
            self.lbl_active.show()
        self.patient_selected.emit(pid)

    def set_patient(self, patient_id: int):
        """Forcer la sélection d'un patient (appelé depuis le dashboard)."""
        for i in range(self.cb_patient.count()):
            if self.cb_patient.itemData(i) == patient_id:
                self.cb_patient.setCurrentIndex(i)
                self._current_id = patient_id
                self._on_load()
                return
        # Si pas encore dans la liste, recharger
        self._load_patients()
        for i in range(self.cb_patient.count()):
            if self.cb_patient.itemData(i) == patient_id:
                self.cb_patient.setCurrentIndex(i)
                self._current_id = patient_id
                self._on_load()
                return
