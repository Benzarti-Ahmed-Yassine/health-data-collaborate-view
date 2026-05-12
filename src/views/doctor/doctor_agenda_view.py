from ...utils.qt_compat import QtWidgets, QtCore, QtGui
from ...core.app import SmartMedicalApp

class DoctorAgendaView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header_layout = QtWidgets.QHBoxLayout()
        header = QtWidgets.QLabel("📅 Mon Agenda")
        header.setStyleSheet("font-size: 20pt; font-weight: bold; color: #1890ff;")
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        self.calendar_btn = QtWidgets.QPushButton("📅 Filtrer par date")
        self.calendar_btn.clicked.connect(self._on_choose_date)
        header_layout.addWidget(self.calendar_btn)
        
        self.btn_all = QtWidgets.QPushButton("🔄 Tout voir")
        self.btn_all.clicked.connect(self._on_show_all)
        header_layout.addWidget(self.btn_all)

        self.btn_add = QtWidgets.QPushButton("🆕 Nouveau RDV")
        self.btn_add.setStyleSheet("background-color: #1890ff; color: white; font-weight: bold; padding: 5px 15px; border-radius: 6px;")
        self.btn_add.clicked.connect(self._on_add_appointment)
        header_layout.addWidget(self.btn_add)
        
        layout.addLayout(header_layout)

        # Appointments Table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date / Heure", "Patient", "Motif", "Statut", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("background-color: white; border-radius: 8px;")
        layout.addWidget(self.table)

        self.selected_date = None
        self._load_agenda()

    def _load_agenda(self):
        try:
            # Charger les RDV du médecin connecté
            doctor_id = self.app.current_user_id()
            
            if self.selected_date:
                query = """
                    SELECT a.id, a.scheduled_date, a.scheduled_time, p.first_name, p.last_name, a.status
                    FROM appointments a
                    JOIN patients p ON a.patient_id = p.id
                    WHERE a.doctor_id = ? AND a.scheduled_date = ?
                    ORDER BY a.scheduled_time ASC
                """
                rdvs = self.app.db.fetch_all(query, (doctor_id, self.selected_date))
            else:
                query = """
                    SELECT a.id, a.scheduled_date, a.scheduled_time, p.first_name, p.last_name, a.status
                    FROM appointments a
                    JOIN patients p ON a.patient_id = p.id
                    WHERE a.doctor_id = ?
                    ORDER BY a.scheduled_date DESC, a.scheduled_time ASC
                """
                rdvs = self.app.db.fetch_all(query, (doctor_id,))

            self.table.setRowCount(len(rdvs))
            for i, r in enumerate(rdvs):
                date_str = f"{r['scheduled_date']} {r.get('scheduled_time', '')}"
                self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(date_str))
                self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(f"{r['first_name']} {r['last_name']}"))
                self.table.setItem(i, 2, QtWidgets.QTableWidgetItem("Consultation standard"))
                
                status_item = QtWidgets.QTableWidgetItem(r['status'])
                if r['status'] == 'CONFIRMED':
                    status_item.setForeground(QtGui.QColor("#52c41a"))
                elif r['status'] == 'CANCELLED':
                    status_item.setForeground(QtGui.QColor("#ff4d4f"))
                
                self.table.setItem(i, 3, status_item)
                
                # Actions Container
                actions = QtWidgets.QWidget()
                al = QtWidgets.QHBoxLayout(actions)
                al.setContentsMargins(0,0,0,0)
                
                btn_del = QtWidgets.QPushButton("🗑️")
                btn_del.setFixedWidth(30)
                btn_del.clicked.connect(lambda checked, aid=r['id']: self._on_delete_appointment(aid))
                al.addWidget(btn_del)
                
                self.table.setCellWidget(i, 4, actions)
                
        except Exception as e:
            print(f"Error loading agenda: {e}")

    def _on_choose_date(self):
        # Création d'un calendrier simple dans un dialogue
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Choisir une date")
        lay = QtWidgets.QVBoxLayout(dialog)
        cal = QtWidgets.QCalendarWidget()
        lay.addWidget(cal)
        
        btn = QtWidgets.QPushButton("Filtrer")
        btn.clicked.connect(dialog.accept)
        lay.addWidget(btn)
        
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.selected_date = cal.selectedDate().toString("yyyy-MM-dd")
            self.calendar_btn.setText(f"📅 {self.selected_date}")
            self._load_agenda()

    def _on_show_all(self):
        self.selected_date = None
        self.calendar_btn.setText("📅 Filtrer par date")
        self._load_agenda()

    def _on_add_appointment(self):
        # On peut réutiliser la même logique ou importer de secretary
        from ..secretary.secretary_agenda_view import AppointmentDialog
        dialog = AppointmentDialog(self)
        # Forcer le médecin actuel
        index = dialog.cb_doctor.findData(self.app.current_user_id())
        if index >= 0:
            dialog.cb_doctor.setCurrentIndex(index)
            dialog.cb_doctor.setEnabled(False)
            
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if self.app.db.insert("appointments", data):
                self._load_agenda()

    def _on_delete_appointment(self, aid):
        if QtWidgets.QMessageBox.question(self, "Confirmer", "Supprimer ce rendez-vous ?") == QtWidgets.QMessageBox.StandardButton.Yes:
            if self.app.db.delete("appointments", aid):
                self._load_agenda()

