from ...utils.qt_compat import QtWidgets, QtCore, QtGui
from ...core.app import SmartMedicalApp
import os

class PatientPrescriptionsView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header = QtWidgets.QLabel("💊 Mes Ordonnances")
        header.setStyleSheet("font-size: 20pt; font-weight: bold; color: #fa8c16;")
        layout.addWidget(header)

        # Description
        desc = QtWidgets.QLabel("Consultez et téléchargez vos ordonnances au format PDF.")
        desc.setStyleSheet("color: #0050b3; font-size: 10pt;")
        layout.addWidget(desc)

        # Table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Date", "Médecin", "Document", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white; 
                border-radius: 12px; 
                border: 1px solid #f0f0f0;
            }
        """)
        layout.addWidget(self.table)

        self._load_prescriptions()

    def _load_prescriptions(self):
        try:
            patient_id = self.app.current_user_id()
            
            # On récupère les documents PDF de type ORDONNANCE pour ce patient
            query = """
                SELECT d.id, d.created_at, d.file_path, u.full_name as doctor_name
                FROM medical_documents d
                LEFT JOIN users u ON u.role = 'DOCTOR' -- Idéalement joint via consultation_id, mais on simplifie ici
                WHERE d.patient_id = ? AND d.category = 'ORDONNANCE'
                ORDER BY d.created_at DESC
            """
            # Note: Si vous n'avez pas de lien direct, on affiche les docs du patient
            docs = self.app.db.fetch_all("SELECT id, created_at, file_path FROM medical_documents WHERE patient_id = ? AND category = 'ORDONNANCE' ORDER BY created_at DESC", (patient_id,))
            
            self.table.setRowCount(len(docs))
            for i, d in enumerate(docs):
                date_str = d['created_at'][:10] if d['created_at'] else "--"
                self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(date_str))
                self.table.setItem(i, 1, QtWidgets.QTableWidgetItem("Dr. Ahmed Yassine")) # Placeholder si non joint
                
                filename = os.path.basename(d['file_path'])
                self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(filename))
                
                # Bouton Voir
                btn_view = QtWidgets.QPushButton("👁️ Ouvrir PDF")
                btn_view.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
                btn_view.setStyleSheet("color: #fa8c16; font-weight: bold; background: transparent;")
                btn_view.clicked.connect(lambda checked, path=d['file_path']: self._open_pdf(path))
                self.table.setCellWidget(i, 3, btn_view)

            if not docs:
                self.table.setRowCount(1)
                self.table.setSpan(0, 0, 1, 4)
                self.table.setItem(0, 0, QtWidgets.QTableWidgetItem("Aucune ordonnance PDF disponible."))
                self.table.item(0, 0).setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        except Exception as e:
            print(f"Error loading patient prescriptions: {e}")

    def _open_pdf(self, path):
        if os.path.exists(path):
            try:
                os.startfile(path)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Erreur", f"Impossible d'ouvrir le fichier : {e}")
        else:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Le fichier est introuvable sur votre appareil.")
