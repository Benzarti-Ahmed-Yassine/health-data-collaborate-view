from ...utils.qt_compat import QtWidgets, QtCore, QtGui
from ...core.app import SmartMedicalApp

class SecretaryAgendaView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header = QtWidgets.QLabel("📅 Calendrier Clinique Global")
        header.setStyleSheet("font-size: 20pt; font-weight: bold; color: #13c2c2;")
        layout.addWidget(header)

        # Filters & Actions
        filter_layout = QtWidgets.QHBoxLayout()
        self.combo_doctor = QtWidgets.QComboBox()
        self.combo_doctor.addItem("Tous les médecins")
        self.combo_doctor.setFixedWidth(200)
        filter_layout.addWidget(self.combo_doctor)
        
        filter_layout.addStretch()
        
        self.btn_add = QtWidgets.QPushButton("🆕 Nouveau RDV")
        self.btn_add.setStyleSheet("background-color: #13c2c2; color: white; font-weight: bold; padding: 8px 15px; border-radius: 6px;")
        self.btn_add.clicked.connect(self._on_add_appointment)
        filter_layout.addWidget(self.btn_add)
        
        layout.addLayout(filter_layout)

        # Agenda Table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Heure", "Médecin", "Patient", "Motif", "Statut", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("background-color: white; border-radius: 8px;")
        layout.addWidget(self.table)

        self._load_global_agenda()

    def _load_global_agenda(self):
        try:
            today = QtCore.QDate.currentDate().toString("yyyy-MM-dd")
            query = """
                SELECT a.id, a.scheduled_date, u.full_name as doctor_name, p.id as patient_id, p.first_name, p.last_name, a.status, a.pending_date, a.pending_time
                FROM appointments a
                JOIN users u ON a.doctor_id = u.id
                JOIN patients p ON a.patient_id = p.id
                ORDER BY a.scheduled_date DESC
            """
            rdvs = self.app.db.fetch_all(query)
            self.table.setRowCount(len(rdvs))
            for i, r in enumerate(rdvs):
                date_val = r['scheduled_date']
                if r['status'] == 'CHANGE_REQUESTED':
                    date_val = f"⚠️ {r['scheduled_date']} -> {r['pending_date']} {r['pending_time']}"
                
                self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(date_val))
                self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(r['doctor_name']))
                self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{r['first_name']} {r['last_name']}"))
                self.table.setItem(i, 3, QtWidgets.QTableWidgetItem("Consultation"))
                
                status_item = QtWidgets.QTableWidgetItem(r['status'])
                if r['status'] == 'CHANGE_REQUESTED':
                    status_item.setForeground(QtGui.QColor("#ff4d4f"))
                    status_item.setText("🚨 DEMANDE CHANGEMENT")
                self.table.setItem(i, 4, status_item)
                
                # Actions
                actions = QtWidgets.QWidget()
                al = QtWidgets.QHBoxLayout(actions)
                al.setContentsMargins(0, 0, 0, 0)
                al.setSpacing(4)
                
                if r['status'] == 'CHANGE_REQUESTED':
                    btn_approve = QtWidgets.QPushButton("✅")
                    btn_approve.setToolTip("Approuver le changement")
                    btn_approve.clicked.connect(lambda checked, aid=r['id'], rd=r: self._on_approve_change(aid, rd))
                    al.addWidget(btn_approve)
                
                # Dossier button
                btn_dos = QtWidgets.QPushButton("📁")
                btn_dos.setFixedWidth(30)
                btn_dos.setToolTip("Ouvrir le Dossier")
                btn_dos.clicked.connect(lambda checked, pid=r['patient_id']: self._on_open_dossier(pid))
                al.addWidget(btn_dos)

                btn_edit = QtWidgets.QPushButton("✏️")
                btn_edit.setFixedWidth(30)
                btn_edit.clicked.connect(lambda checked, aid=r['id']: self._on_edit_appointment(aid))
                al.addWidget(btn_edit)
                
                btn_del = QtWidgets.QPushButton("🗑️")
                btn_del.setFixedWidth(30)
                btn_del.clicked.connect(lambda checked, aid=r['id']: self._on_delete_appointment(aid))
                al.addWidget(btn_del)
                self.table.setCellWidget(i, 5, actions)
                
        except Exception as e:
            print(f"Error loading global agenda: {e}")

    def _on_open_dossier(self, patient_id):
        win = self.window()
        if hasattr(win, "open_patient_dossier"):
            win.open_patient_dossier(patient_id)

    def _on_approve_change(self, aid, r):
        if QtWidgets.QMessageBox.question(self, "Approuver", f"Accepter le changement pour {r['first_name']} ?") == QtWidgets.QMessageBox.StandardButton.Yes:
            new_date = f"{r['pending_date']} {r['pending_time']}"
            data = {
                "scheduled_date": new_date,
                "status": "CONFIRMED",
                "pending_date": None,
                "pending_time": None
            }
            if self.app.db.update("appointments", aid, data):
                self._load_global_agenda()

    def _on_add_appointment(self):
        dialog = AppointmentDialog(self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if self.app.db.insert("appointments", data):
                QtWidgets.QMessageBox.information(self, "Succès", "Rendez-vous ajouté.")
                self._load_global_agenda()

    def _on_edit_appointment(self, aid):
        apt_data = self.app.db.get_by_id("appointments", aid)
        if not apt_data: return
        dialog = AppointmentDialog(self, apt_data)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if self.app.db.update("appointments", aid, data):
                self._load_global_agenda()

    def _on_delete_appointment(self, aid):
        if QtWidgets.QMessageBox.question(self, "Confirmer", "Supprimer ce rendez-vous ?") == QtWidgets.QMessageBox.StandardButton.Yes:
            if self.app.db.delete("appointments", aid):
                self._load_global_agenda()

class AppointmentDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, apt_data=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self.apt_data = apt_data
        self.setWindowTitle("Modifier le Rendez-vous" if apt_data else "Nouveau Rendez-vous")
        self.setFixedWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        l = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        
        self.cb_patient = QtWidgets.QComboBox()
        patients = self.app.db.fetch_all("SELECT id, first_name, last_name FROM patients WHERE is_active=1")
        for p in patients: self.cb_patient.addItem(f"{p['first_name']} {p['last_name']}", p['id'])
        form.addRow("Patient:", self.cb_patient)
        
        self.cb_doctor = QtWidgets.QComboBox()
        doctors = self.app.db.fetch_all("SELECT id, full_name FROM users WHERE role='DOCTOR'")
        for d in doctors: self.cb_doctor.addItem(d['full_name'], d['id'])
        form.addRow("Médecin:", self.cb_doctor)
        
        self.dt_date = QtWidgets.QDateTimeEdit(QtCore.QDateTime.currentDateTime())
        self.dt_date.setCalendarPopup(True)
        form.addRow("Date & Heure:", self.dt_date)
        
        if self.apt_data:
            idx_p = self.cb_patient.findData(self.apt_data['patient_id'])
            if idx_p >= 0: self.cb_patient.setCurrentIndex(idx_p)
            idx_d = self.cb_doctor.findData(self.apt_data['doctor_id'])
            if idx_d >= 0: self.cb_doctor.setCurrentIndex(idx_d)
            dt = QtCore.QDateTime.fromString(self.apt_data['scheduled_date'], "yyyy-MM-dd HH:mm:ss")
            if dt.isValid(): self.dt_date.setDateTime(dt)

        l.addLayout(form)
        
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        l.addWidget(btns)

    def get_data(self):
        dt = self.dt_date.dateTime()
        return {
            "patient_id":     self.cb_patient.currentData(),
            "doctor_id":      self.cb_doctor.currentData(),
            "scheduled_date": dt.toString("yyyy-MM-dd"),
            "scheduled_time": dt.toString("HH:mm"),
            "status":         "CONFIRMED",
            "arrived":        0,
            "reminder_sent":  0,
        }

