from ...utils.qt_compat import QtWidgets, QtCore
from ...core.app import SmartMedicalApp
from ..components import KPICard

class SecretaryDashboardView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        header = QtWidgets.QLabel("📊 Gestion de l'Accueil & Facturation")
        header.setStyleSheet("font-size: 20pt; font-weight: bold; color: #13c2c2;")
        main_layout.addWidget(header)

        # Stats
        self.stats_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(self.stats_layout)

        # Split: Appointments and Actions
        split = QtWidgets.QHBoxLayout()
        
        # Left: Quick Access
        actions = QtWidgets.QFrame()
        actions.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #f0f0f0;")
        act_layout = QtWidgets.QVBoxLayout(actions)
        act_layout.addWidget(QtWidgets.QLabel("⚡ Actions Rapides"))
        
        self.btn1 = QtWidgets.QPushButton("🆕 Nouveau Patient")
        self.btn2 = QtWidgets.QPushButton("📅 Prendre Rendez-vous")
        self.btn3 = QtWidgets.QPushButton("💰 Créer Facture")
        
        for b in [self.btn1, self.btn2, self.btn3]:
            b.setFixedHeight(45)
            b.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet("background-color: #f0f5ff; border: 1px solid #adc6ff; border-radius: 8px; color: #1d39c4; font-weight: 500;")
            act_layout.addWidget(b)
        
        # Connect signals
        self.btn1.clicked.connect(self._on_new_patient)
        self.btn2.clicked.connect(self._on_new_appointment)
        self.btn3.clicked.connect(self._on_new_invoice)
        
        act_layout.addStretch()
        split.addWidget(actions, 1)

        # Right: Daily List
        list_frame = QtWidgets.QFrame()
        list_frame.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #f0f0f0;")
        list_layout = QtWidgets.QVBoxLayout(list_frame)
        list_layout.addWidget(QtWidgets.QLabel("🕒 File d'attente / RDV Prochains"))
        
        self.table_rdv = QtWidgets.QTableWidget(0, 4)
        self.table_rdv.setHorizontalHeaderLabels(["Heure", "Patient", "Statut", "Action"])
        self.table_rdv.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table_rdv.setStyleSheet("border: none;")
        list_layout.addWidget(self.table_rdv)
        
        split.addWidget(list_frame, 2)
        main_layout.addLayout(split)
        main_layout.addStretch()

        self.refresh_data()

        # Timer pour rafraîchissement périodique (Temps Réel)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(10000) # Toutes les 10 secondes

        # Abonnement aux événements
        from ...core.events import EventType
        self.app.events.subscribe(EventType.APPOINTMENT_CREATED, lambda _: self.refresh_data())
        self.app.events.subscribe(EventType.INVOICE_CREATED, lambda _: self.refresh_data())

    def refresh_data(self):
        # Clear stats
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        # Stats réelles
        today = QtCore.QDate.currentDate().toString("yyyy-MM-dd")
        rdv_today = len(self.app.db.fetch_all("SELECT id FROM appointments WHERE scheduled_date = ?", (today,)))
        arrived_today = len(self.app.db.fetch_all("SELECT id FROM appointments WHERE scheduled_date = ? AND arrived = 1", (today,)))
        unpaid = len(self.app.db.fetch_all("SELECT id FROM invoices WHERE status = 'En attente'"))

        self.stats_layout.addWidget(KPICard("RDV d'aujourd'hui", str(rdv_today), f"{arrived_today} arrivés", "#13c2c2"))
        self.stats_layout.addWidget(KPICard("Paiements en attente", str(unpaid), "Relances nécessaires", "#fa8c16"))
        self.stats_layout.addWidget(KPICard("Mouvement Global", "Analysé", "Voir Rapport Admin", "#52c41a"))
        self.stats_layout.addStretch()

        # Liste RDV (Heure, Patient, Statut, Action)
        query = """
            SELECT a.id, a.scheduled_time, p.id as patient_id, p.first_name, p.last_name, a.status, a.arrived 
            FROM appointments a 
            JOIN patients p ON a.patient_id = p.id 
            WHERE a.scheduled_date = ? 
            ORDER BY a.scheduled_time ASC
        """
        rdvs = self.app.db.fetch_all(query, (today,))
        self.table_rdv.setRowCount(len(rdvs))
        for i, r in enumerate(rdvs):
            self.table_rdv.setItem(i, 0, QtWidgets.QTableWidgetItem(r['scheduled_time']))
            self.table_rdv.setItem(i, 1, QtWidgets.QTableWidgetItem(f"{r['first_name']} {r['last_name']}"))
            self.table_rdv.setItem(i, 2, QtWidgets.QTableWidgetItem("Arrivé ✅" if r['arrived'] else r['status']))
            
            # Actions Container
            actions_widget = QtWidgets.QWidget()
            actions_layout = QtWidgets.QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)

            # Button Dossier
            btn_dos = QtWidgets.QPushButton("📁 Dossier")
            btn_dos.setStyleSheet("background-color: #1890ff; color: white; border-radius: 4px; padding: 2px 8px;")
            btn_dos.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            btn_dos.clicked.connect(lambda checked, pid=r['patient_id']: self._on_open_dossier(pid))
            actions_layout.addWidget(btn_dos)

            if not r['arrived']:
                btn_arr = QtWidgets.QPushButton("Arrivée")
                btn_arr.setStyleSheet("background-color: #52c41a; color: white; border-radius: 4px; padding: 2px 8px;")
                btn_arr.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
                btn_arr.clicked.connect(lambda checked, aid=r['id']: self._confirm_arrival(aid))
                actions_layout.addWidget(btn_arr)
            
            self.table_rdv.setCellWidget(i, 3, actions_widget)

    def _on_open_dossier(self, patient_id):
        win = self.window()
        if hasattr(win, "open_patient_dossier"):
            win.open_patient_dossier(patient_id)

    def _confirm_arrival(self, appt_id):
        # 1. Récupérer les infos (Patient et Docteur)
        query = """
            SELECT p.first_name, p.last_name, u.email as doctor_email, u.full_name as doctor_name, a.scheduled_time
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN users u ON a.doctor_id = u.id
            WHERE a.id = ?
        """
        info = self.app.db.fetch_one(query, (appt_id,))
        
        if self.app.db.execute("UPDATE appointments SET arrived = 1 WHERE id = ?", (appt_id,)):
            from ...core.events import EventType
            self.app.events.emit(EventType.PATIENT_ARRIVED, appt_id)
            self.refresh_data()
            print(f"[Sec] Arrivée confirmée pour RDV {appt_id}")
            
            # 2. Envoyer notification email au docteur
            if info and info['doctor_email']:
                from ...services.email_service import email_service
                subject = f"🔔 Patient Arrivé : {info['first_name']} {info['last_name']}"
                body = f"Bonjour {info['doctor_name']},\n\nVotre patient {info['first_name']} {info['last_name']} vient d'arriver pour son rendez-vous de {info['scheduled_time']}.\n\nL'assistant a été notifié pour la prise des constantes."
                email_service.send_email(info['doctor_email'], subject, body)


    def _on_new_patient(self):
        from ..patient_view import AddPatientDialog
        from ...core.events import EventType
        dialog = AddPatientDialog(self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if self.app.db.insert("patients", data):
                self.app.events.emit(EventType.PATIENT_CREATED, data)
                QtWidgets.QMessageBox.information(self, "Succès", "Patient ajouté.")
                self.refresh_data()

    def _on_new_appointment(self):
        from .secretary_agenda_view import AppointmentDialog
        from ...core.events import EventType
        dialog = AppointmentDialog(self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if self.app.db.insert("appointments", data):
                self.app.events.emit(EventType.APPOINTMENT_CREATED, data)
                QtWidgets.QMessageBox.information(self, "Succès", "Rendez-vous ajouté.")
                self.refresh_data()

    def _on_new_invoice(self):
        from .secretary_billing_view import InvoiceDialog
        from ...core.events import EventType
        dialog = InvoiceDialog(self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if self.app.db.insert("invoices", data):
                self.app.events.emit(EventType.INVOICE_CREATED, data)
                QtWidgets.QMessageBox.information(self, "Succès", "Facture créée.")
                self.refresh_data()

