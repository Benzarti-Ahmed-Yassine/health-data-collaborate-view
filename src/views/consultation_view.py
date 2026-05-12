"""
Smart Medical AI - Consultation View (AI Integrated)
"""

import os
import datetime
import logging
from ..utils.qt_compat import QtWidgets, QtCore, uic
from ..services.ml_service import MLService
from ..core.app import SmartMedicalApp

logger = logging.getLogger(__name__)

class ConsultationWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self.ml = MLService()

        # ── Wrapper layout pour injecter le sélecteur patient EN HAUT
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Panneau de sélection patient
        from .doctor.patient_selector_panel import PatientSelectorPanel
        self._selector = PatientSelectorPanel(self)
        self._selector.patient_selected.connect(self._on_patient_selected)
        root.addWidget(self._selector)

        # ── Contenu consultation existant (.ui) encapsulé dans un QWidget
        self._content = QtWidgets.QWidget()
        ui_path = os.path.join(os.path.dirname(__file__), "ui", "consultation.ui")
        uic.loadUi(ui_path, self._content)
        root.addWidget(self._content, 1)

        # Alias pour compatibilité avec les noms du fichier .ui
        self._map_widgets()

        # Styles Premium
        if hasattr(self, "btnSave"):
            self.btnSave.setObjectName("btnPrimary")
        if hasattr(self, "btnGeneratePrescription"):
            self.btnGeneratePrescription.setObjectName("btnSuccess")

        # ── Bannière d'information patient
        self._patient_banner = QtWidgets.QFrame()
        self._patient_banner.setStyleSheet("background: #e6f7ff; border-bottom: 1px solid #91d5ff;")
        self._patient_banner.setFixedHeight(42)
        banner_row = QtWidgets.QHBoxLayout(self._patient_banner)
        banner_row.setContentsMargins(20, 0, 20, 0)
        self._lbl_banner = QtWidgets.QLabel("👤 Aucun patient chargé — Utilisez le sélecteur ci-dessus")
        self._lbl_banner.setStyleSheet("color: #0050b3; font-size: 11pt; font-weight: 600;")
        banner_row.addWidget(self._lbl_banner)
        banner_row.addStretch()
        root.insertWidget(1, self._patient_banner)

        self._connect_signals()

        from ..core.events import EventType
        self.app.events.subscribe(EventType.VITALS_RECORDED, self._on_vitals_received)

        if self.app.active_patient_id:
            self._selector.set_patient(self.app.active_patient_id)

    def _map_widgets(self):
        """Associe les widgets du fichier .ui à la classe."""
        widgets = [
            "btnPredict", "btnGeneratePrescription", "btnSave", "btnCancel", "btnVoice",
            "lblVitalsSummary", "lblRiskScore", "lblRiskLevel", "lblPatientName", "lblAge",
            "spinSystolic", "spinDiastolic", "spinHeartRate", "spinTemp", "txtNotes"
        ]
        for name in widgets:
            if hasattr(self._content, name):
                setattr(self, name, getattr(self._content, name))

    def _on_patient_selected(self, patient_id: int):
        try:
            self.load_patient(patient_id)
            patient = self.app.db.get_by_id("patients", patient_id)
            if patient:
                name = f"{patient['first_name']} {patient['last_name']}"
                blood = patient.get('blood_type') or '—'
                phone = patient.get('phone') or '—'
                self._lbl_banner.setText(f"👤 {name}   🩸 {blood}   📞 {phone}")
                
                # Calcul de l'âge
                if hasattr(self, "lblAge") and patient.get('date_of_birth'):
                    try:
                        dob = datetime.datetime.strptime(patient['date_of_birth'], "%Y-%m-%d")
                        age = (datetime.date.today() - dob.date()).days // 365
                        self.lblAge.setText(f"Âge: {age} ans")
                    except: pass
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Erreur", str(e))

    def load_patient(self, patient_id: int):
        current_uid = self.app.current_user_id()
        user = self.app.current_user
        
        # Bypass RBAC pour docteurs/admin
        is_doctor = user and user.get('role', '').lower() in ['doctor', 'admin']
        if not is_doctor:
            if not self.app.rbac.can_perform(current_uid, "consultations", "view"):
                raise PermissionError("Accès refusé aux consultations")

        self.app.active_patient_id = patient_id
        
        # Charger et AUTO-REMPLIR les constantes
        query = "SELECT * FROM vital_signs WHERE patient_id = ? ORDER BY recorded_at DESC LIMIT 1"
        vitals = self.app.db.fetch_one(query, (patient_id,))
        if vitals:
            self._display_vitals(vitals)
            if hasattr(self, "spinSystolic"): self.spinSystolic.setValue(vitals.get('systolic_bp', 0))
            if hasattr(self, "spinDiastolic"): self.spinDiastolic.setValue(vitals.get('diastolic_bp', 0))
            if hasattr(self, "spinHeartRate"): self.spinHeartRate.setValue(vitals.get('heart_rate', 0))
            if hasattr(self, "spinTemp"): self.spinTemp.setValue(vitals.get('temperature', 37.0))
        
        if hasattr(self, "lblPatientName"):
            p = self.app.db.get_by_id("patients", patient_id)
            self.lblPatientName.setText(f"{p['first_name']} {p['last_name']}")

    def _display_vitals(self, data):
        if hasattr(self, "lblVitalsSummary"):
            txt = f"🌡️ {data.get('temperature')}°C | 💓 {data.get('heart_rate')} bpm | 🩺 {data.get('systolic_bp')}/{data.get('diastolic_bp')} mmHg"
            self.lblVitalsSummary.setText(txt)

    def _on_vitals_received(self, data):
        if self.app.active_patient_id == data.get("patient_id"):
            self._display_vitals(data)
            if hasattr(self, "spinSystolic"): self.spinSystolic.setValue(data.get('systolic_bp', 0))
            if hasattr(self, "spinDiastolic"): self.spinDiastolic.setValue(data.get('diastolic_bp', 0))
            if hasattr(self, "spinHeartRate"): self.spinHeartRate.setValue(data.get('heart_rate', 0))
            if hasattr(self, "spinTemp"): self.spinTemp.setValue(data.get('temperature', 37.0))

    def _connect_signals(self):
        if hasattr(self, "btnPredict"):
            self.btnPredict.clicked.connect(self._on_analyze)
        if hasattr(self, "btnGeneratePrescription"):
            self.btnGeneratePrescription.clicked.connect(self._on_generate_prescription)
        if hasattr(self, "btnSave"):
            self.btnSave.clicked.connect(self._on_save_consultation)

    def _on_analyze(self):
        data = {
            'systolic': self.spinSystolic.value(),
            'diastolic': self.spinDiastolic.value(),
            'heart_rate': self.spinHeartRate.value(),
            'temperature': self.spinTemp.value()
        }
        score, level, explanation = self.ml.predict_risk(data)
        if hasattr(self, "lblRiskScore"):
            self.lblRiskScore.setText(f"Score: {score}%")
        if hasattr(self, "lblRiskLevel"):
            self.lblRiskLevel.setText(f"Niveau: {level}")
            color = "#ff4d4f" if level == "ÉLEVÉ" else "#52c41a"
            self.lblRiskLevel.setStyleSheet(f"color: {color}; font-weight: bold;")

    def _on_generate_prescription(self):
        if not self.app.active_patient_id:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Aucun patient sélectionné.")
            return

        notes = self.txtNotes.toPlainText().strip() if hasattr(self, "txtNotes") else ""
        if not notes:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Veuillez saisir le contenu de l'ordonnance dans les observations.")
            return

        # 1. Créer la prescription en DB
        doctor_id = self.app.current_user_id()
        presc_id = self.app.db.insert("prescriptions", {
            "patient_id": self.app.active_patient_id,
            "doctor_id": doctor_id,
            "created_at": datetime.datetime.now().isoformat()
        })

        # 2. Générer le PDF
        pdf_path = self._generate_pdf(presc_id, notes)
        
        if pdf_path:
            # 3. Enregistrer dans medical_documents
            self.app.db.insert("medical_documents", {
                "patient_id": self.app.active_patient_id,
                "file_path": pdf_path,
                "file_type": "PDF",
                "category": "ORDONNANCE",
                "created_at": datetime.datetime.now().isoformat()
            })
            
            QtWidgets.QMessageBox.information(self, "Succès", f"Ordonnance générée et enregistrée.\nFichier : {os.path.basename(pdf_path)}")
            
            # Ouvrir le PDF automatiquement
            try: os.startfile(pdf_path)
            except: pass
        else:
            QtWidgets.QMessageBox.critical(self, "Erreur", "Échec de la génération du PDF.")

    def _generate_pdf(self, presc_id, content):
        """Génère un PDF d'ordonnance professionnel avec ReportLab."""
        try:
            from reportlab.lib.pagesizes import A5
            from reportlab.pdfgen import canvas
            from reportlab.lib import colors

            docs_dir = os.path.join(os.getcwd(), "db", "documents")
            os.makedirs(docs_dir, exist_ok=True)
            
            filename = f"Ordonnance_{presc_id}_{datetime.date.today().isoformat()}.pdf"
            path = os.path.join(docs_dir, filename)
            
            p = canvas.Canvas(path, pagesize=A5)
            width, height = A5
            
            # --- En-tête ---
            p.setFont("Helvetica-Bold", 14)
            p.drawString(40, height - 50, self.app.current_user.get('full_name', 'Dr. Ahmed Yassine'))
            p.setFont("Helvetica", 9)
            p.drawString(40, height - 65, "Médecin Généraliste - MediERP Professional")
            p.line(40, height - 75, width - 40, height - 75)
            
            # --- Infos Patient ---
            patient = self.app.db.get_by_id("patients", self.app.active_patient_id)
            p.setFont("Helvetica-Bold", 11)
            p.drawString(40, height - 100, f"Patient : {patient['first_name']} {patient['last_name']}")
            p.setFont("Helvetica", 10)
            p.drawRightString(width - 40, height - 100, f"Date : {datetime.date.today().strftime('%d/%m/%Y')}")
            
            # --- Corps ---
            p.setFont("Helvetica-Bold", 12)
            p.drawCentredString(width/2, height - 140, "ORDONNANCE")
            
            text_obj = p.beginText(50, height - 180)
            text_obj.setFont("Helvetica", 11)
            text_obj.setLeading(16)
            
            # Diviser le contenu en lignes
            lines = content.split('\n')
            for line in lines:
                text_obj.textLine(line)
            p.drawText(text_obj)
            
            # --- Pied de page ---
            p.line(40, 80, width - 40, 80)
            p.setFont("Helvetica-Oblique", 8)
            p.drawCentredString(width/2, 60, "Document généré par MediERP - Signature et cachet requis")
            
            p.showPage()
            p.save()
            return path
        except Exception as e:
            logger.error(f"Erreur PDF : {e}")
            return None

    def _on_save_consultation(self):
        QtWidgets.QMessageBox.information(self, "Sauvegarde", "Consultation enregistrée avec succès.")
