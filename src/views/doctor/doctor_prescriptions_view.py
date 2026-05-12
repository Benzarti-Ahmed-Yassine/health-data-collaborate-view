from ...utils.qt_compat import QtWidgets, QtCore, QtGui
from ...core.app import SmartMedicalApp
import os

class DoctorPrescriptionsView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("💊 Historique des Ordonnances")
        title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #1890ff;")
        header.addWidget(title)
        header.addStretch()
        
        self.btn_refresh = QtWidgets.QPushButton("🔄 Actualiser")
        self.btn_refresh.setStyleSheet("padding: 8px 15px; background: white; border: 1px solid #d9d9d9; border-radius: 6px;")
        self.btn_refresh.clicked.connect(self._load_data)
        header.addWidget(self.btn_refresh)
        
        layout.addLayout(header)

        # Table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Patient", "Type", "Fichier", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e8e8e8;")
        layout.addWidget(self.table)

        self._load_data()

    def _load_data(self):
        try:
            # Récupérer toutes les ordonnances enregistrées comme documents
            query = """
                SELECT d.id, d.created_at, p.first_name, p.last_name, d.file_path, d.category
                FROM medical_documents d
                JOIN patients p ON d.patient_id = p.id
                WHERE d.category = 'ORDONNANCE'
                ORDER BY d.created_at DESC
            """
            docs = self.app.db.fetch_all(query)
            
            self.table.setRowCount(len(docs))
            for i, d in enumerate(docs):
                date_str = d['created_at'][:16].replace('T', ' ')
                self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(date_str))
                self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(f"{d['first_name']} {d['last_name']}"))
                self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(d['category']))
                
                filename = os.path.basename(d['file_path'])
                self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(filename))
                
                # Actions
                btn_view = QtWidgets.QPushButton("👁️ Voir PDF")
                btn_view.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
                btn_view.setStyleSheet("color: #1890ff; background: transparent; font-weight: bold;")
                btn_view.clicked.connect(lambda checked, path=d['file_path']: self._open_pdf(path))
                self.table.setCellWidget(i, 4, btn_view)

        except Exception as e:
            print(f"Error loading prescriptions docs: {e}")

    def _open_pdf(self, path):
        if os.path.exists(path):
            try:
                os.startfile(path)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Erreur", f"Impossible d'ouvrir le fichier : {e}")
        else:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Le fichier PDF est introuvable sur le disque.")

    def search(self, text):
        """Filtre la table selon le texte de recherche."""
        text = text.lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)
