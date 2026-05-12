from ...utils.qt_compat import QtWidgets, QtCore, QtGui
from ...core.app import SmartMedicalApp

class VitalSignsView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # Header
        header = QtWidgets.QLabel("📋 Saisie des Constantes Vitales")
        header.setStyleSheet("font-size: 20pt; font-weight: bold; color: #52c41a;")
        layout.addWidget(header)

        # Patient Selector (Simplified)
        layout.addWidget(QtWidgets.QLabel("<b>1. Sélectionner le Patient</b>"))
        self.patient_combo = QtWidgets.QComboBox()
        self.patient_combo.addItem("Chargement des patients...")
        layout.addWidget(self.patient_combo)

        # Form
        layout.addWidget(QtWidgets.QLabel("<b>2. Mesures</b>"))
        form_frame = QtWidgets.QFrame()
        form_frame.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #f0f0f0; padding: 20px;")
        form_layout = QtWidgets.QFormLayout(form_frame)
        form_layout.setSpacing(15)

        self.txt_temp = QtWidgets.QLineEdit()
        self.txt_temp.setPlaceholderText("ex: 37.5")
        form_layout.addRow("🌡️ Température (°C):", self.txt_temp)

        self.txt_pulse = QtWidgets.QLineEdit()
        self.txt_pulse.setPlaceholderText("ex: 75")
        form_layout.addRow("💓 Pouls (bpm):", self.txt_pulse)

        self.txt_bp = QtWidgets.QLineEdit()
        self.txt_bp.setPlaceholderText("ex: 120/80")
        form_layout.addRow("🩺 Tension (mmHg):", self.txt_bp)

        self.txt_spo2 = QtWidgets.QLineEdit()
        self.txt_spo2.setPlaceholderText("ex: 98")
        form_layout.addRow("🫁 SpO2 (%):", self.txt_spo2)

        layout.addWidget(form_frame)

        # Buttons
        self.btn_save = QtWidgets.QPushButton("💾 Enregistrer les constantes")
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #52c41a;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover { background-color: #73d13d; }
        """)
        self.btn_save.clicked.connect(self._on_save_vitals)
        layout.addWidget(self.btn_save)
        
        layout.addStretch()
        self._load_patients()

    def _load_patients(self):
        try:
            patients = self.app.db.fetch_all("SELECT id, first_name, last_name FROM patients WHERE is_active=1")
            self.patient_combo.clear()
            for p in patients:
                self.patient_combo.addItem(f"{p['first_name']} {p['last_name']}", p['id'])
        except Exception as e:
            print(f"Error loading patients for vitals: {e}")

    def _on_save_vitals(self):
        patient_id = self.patient_combo.currentData()
        if not patient_id:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un patient.")
            return

        try:
            # On cherche une consultation active pour ce patient ou on crée un log indépendant
            # Pour l'instant, on insère dans vital_signs avec consultation_id = NULL si non précisé
            # Le schéma autorise consultation_id INTEGER (FOREIGN KEY)
            
            # Parsing BP
            bp = self.txt_bp.text().split('/')
            systolic = int(bp[0]) if len(bp) > 0 and bp[0].isdigit() else 120
            diastolic = int(bp[1]) if len(bp) > 1 and bp[1].isdigit() else 80

            last_cons = self.app.db.fetch_one("SELECT id FROM consultations WHERE patient_id=? AND status='IN_PROGRESS' ORDER BY start_time DESC", (patient_id,))
            
            db_data = {
                "consultation_id": last_cons["id"] if last_cons else None,
                "patient_id": patient_id,
                "temperature": float(self.txt_temp.text()) if self.txt_temp.text() else 37.0,
                "heart_rate": int(self.txt_pulse.text()) if self.txt_pulse.text().isdigit() else 70,
                "systolic_bp": systolic,
                "diastolic_bp": diastolic,
                "spo2": float(self.txt_spo2.text()) if self.txt_spo2.text() else 98.0
            }

            new_id = self.app.db.insert("vital_signs", db_data)
            if new_id:
                from ...core.events import EventType
                db_data["patient_id"] = patient_id
                self.app.events.emit(EventType.VITALS_RECORDED, db_data)
                
                QtWidgets.QMessageBox.information(self, "Succès", "Constantes enregistrées avec succès.")
                self.txt_temp.clear()
                self.txt_pulse.clear()
                self.txt_bp.clear()
                self.txt_spo2.clear()
            else:
                QtWidgets.QMessageBox.warning(self, "Erreur", "Erreur lors de l'enregistrement.")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erreur", f"Données invalides : {e}")

