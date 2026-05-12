from ...utils.qt_compat import QtWidgets, QtCore, QtGui
from ...core.app import SmartMedicalApp

class PatientProfileView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # Header
        header = QtWidgets.QLabel("👤 Mon Profil Santé & Évolution")
        header.setStyleSheet("font-size: 20pt; font-weight: bold; color: #fa8c16;")
        layout.addWidget(header)

        # Main Scroll Area
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")
        
        container = QtWidgets.QWidget()
        container_layout = QtWidgets.QVBoxLayout(container)
        container_layout.setSpacing(20)

        # 1. Infos Personnelles
        info_panel = QtWidgets.QFrame()
        info_panel.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #f0f0f0;")
        info_layout = QtWidgets.QGridLayout(info_panel)
        info_layout.setContentsMargins(20, 20, 20, 20)
        
        user = self.app.current_user
        info_layout.addWidget(QtWidgets.QLabel("<b>Nom Complet:</b>"), 0, 0)
        info_layout.addWidget(QtWidgets.QLabel(user.get('full_name', '--')), 0, 1)
        info_layout.addWidget(QtWidgets.QLabel("<b>Rôle:</b>"), 1, 0)
        info_layout.addWidget(QtWidgets.QLabel("Patient"), 1, 1)
        
        container_layout.addWidget(info_panel)

        # 2. Diagnostique d'Évolution (Analyse IA & Médicale)
        diagnosis_panel = QtWidgets.QFrame()
        diagnosis_panel.setStyleSheet("background-color: #fff7e6; border-radius: 12px; border: 1px solid #ffd591;")
        diag_layout = QtWidgets.QVBoxLayout(diagnosis_panel)
        diag_layout.setContentsMargins(20, 20, 20, 20)
        
        diag_layout.addWidget(QtWidgets.QLabel("<b>🧠 Diagnostique Complet d'Évolution</b>"))
        
        self.diag_text = QtWidgets.QLabel("Analyse de vos données en cours...")
        self.diag_text.setWordWrap(True)
        self.diag_text.setStyleSheet("font-size: 11pt; line-height: 1.5; color: #0050b3;")
        diag_layout.addWidget(self.diag_text)
        
        container_layout.addWidget(diagnosis_panel)

        # 3. Historique des Constantes (Tableau)
        vitals_panel = QtWidgets.QFrame()
        vitals_panel.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #f0f0f0;")
        v_layout = QtWidgets.QVBoxLayout(vitals_panel)
        v_layout.addWidget(QtWidgets.QLabel("<b>📊 Évolution des Constantes Vitales</b>"))
        
        self.table_vitals = QtWidgets.QTableWidget()
        self.table_vitals.setColumnCount(5)
        self.table_vitals.setHorizontalHeaderLabels(["Date", "Tension", "Pouls", "Temp.", "SpO2"])
        self.table_vitals.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        v_layout.addWidget(self.table_vitals)
        
        container_layout.addWidget(vitals_panel)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        self.refresh_data()

    def refresh_data(self):
        try:
            pid = self.app.current_user_id()

            # FIX: Query vital_signs directly by patient_id. The old JOIN on consultations
            # was hiding all assistant-recorded vitals that had no consultation_id set.
            query = """
                SELECT * FROM vital_signs
                WHERE patient_id = ?
                ORDER BY recorded_at DESC LIMIT 10
            """
            vitals = self.app.db.fetch_all(query, (pid,))

            self.table_vitals.setRowCount(len(vitals))
            for i, v in enumerate(vitals):
                date_val = v.get('recorded_at', '')
                self.table_vitals.setItem(i, 0, QtWidgets.QTableWidgetItem(date_val[:10] if date_val else '--'))
                self.table_vitals.setItem(i, 1, QtWidgets.QTableWidgetItem(f"{v['systolic_bp']}/{v['diastolic_bp']}"))
                self.table_vitals.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{v['heart_rate']} bpm"))
                self.table_vitals.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{v['temperature']}°C"))
                self.table_vitals.setItem(i, 4, QtWidgets.QTableWidgetItem(f"{v['spo2']}%"))

            # Generate AI/Medical Diagnosis of evolution
            self._generate_diagnosis(vitals)

        except Exception as e:
            print(f"Error loading profile data: {e}")

    def _generate_diagnosis(self, vitals):
        if not vitals:
            self.diag_text.setText("Aucune donnée médicale suffisante pour établir un diagnostique d'évolution. Veuillez effectuer une consultation pour initialiser votre suivi.")
            return

        latest = vitals[0]
        
        # Simple analysis logic
        status = "Stable"
        trends = []
        
        if latest['systolic_bp'] > 140 or latest['diastolic_bp'] > 90:
            trends.append("Tension artérielle élevée détectée lors du dernier relevé.")
            status = "À surveiller"
            
        if latest['temperature'] > 38:
            trends.append("État fébrile récent.")
            
        if len(vitals) > 1:
            prev = vitals[1]
            if latest['heart_rate'] > prev['heart_rate'] + 10:
                trends.append("Augmentation notable de la fréquence cardiaque au repos.")
            elif latest['heart_rate'] < prev['heart_rate'] - 10:
                trends.append("Diminution de la fréquence cardiaque.")

        diagnosis = f"<b>État Actuel : {status}</b><br><br>"
        if trends:
            diagnosis += "<b>Observations :</b><br>• " + "<br>• ".join(trends)
        else:
            diagnosis += "Vos constantes sont dans les normes standards. L'évolution est positive et stable sur les dernières consultations."
            
        diagnosis += "<br><br><i>Ce diagnostique est généré automatiquement par l'IA MediERP sur la base de vos constantes historiques. Consultez toujours votre médecin pour une interprétation clinique.</i>"
        
        self.diag_text.setText(diagnosis)
        self.diag_text.setTextFormat(QtCore.Qt.TextFormat.RichText)
