from ...utils.qt_compat import QtWidgets, QtCore, QtGui
from ...core.app import SmartMedicalApp
from ..components import KPICard

class AssistantDashboardView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        header = QtWidgets.QLabel("📋 Support Médical & Soins")
        header.setStyleSheet("font-size: 20pt; font-weight: bold; color: #52c41a;")
        main_layout.addWidget(header)

        # Cards
        self.stats_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(self.stats_layout)

        # Quick Actions
        qa_panel = QtWidgets.QFrame()
        qa_panel.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #f0f0f0;")
        qa_layout = QtWidgets.QHBoxLayout(qa_panel)
        qa_layout.addWidget(QtWidgets.QLabel("<b>⚡ Actions:</b>"))
        
        btn_vitals = QtWidgets.QPushButton("📋 Prendre Constantes")
        btn_pat = QtWidgets.QPushButton("👥 Patients")
        
        for b in [btn_vitals, btn_pat]:
            b.setFixedHeight(40)
            b.setStyleSheet("background-color: #f6ffed; color: #52c41a; border: 1px solid #b7eb8f; border-radius: 8px; font-weight: 500; padding: 0 15px;")
            b.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            qa_layout.addWidget(b)
            
        btn_vitals.clicked.connect(lambda: self._navigate_to("asst_vitals"))
        btn_pat.clicked.connect(lambda: self._navigate_to("asst_patients"))
        
        main_layout.addWidget(qa_panel)

        # Tasks List
        tasks = QtWidgets.QFrame()
        tasks.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #f0f0f0;")
        task_layout = QtWidgets.QVBoxLayout(tasks)
        task_layout.addWidget(QtWidgets.QLabel("📝 Ma Liste de Tâches"))
        
        self.list_tasks = QtWidgets.QListWidget()
        self.list_tasks.setStyleSheet("""
            QListWidget { border: none; font-size: 11pt; color: #141414; padding: 10px; }
            QListWidget::item { padding: 8px; border-bottom: 1px solid #f0f0f0; }
            QListWidget::item:hover { background-color: #f6ffed; }
            QListWidget::indicator { width: 20px; height: 20px; }
        """)
        self.list_tasks.itemChanged.connect(self._on_task_changed)
        task_layout.addWidget(self.list_tasks)
        
        main_layout.addWidget(tasks)
        main_layout.addStretch()

        self.refresh_data()

        # Temps Réel
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(10000)

        from ...core.events import EventType
        self.app.events.subscribe(EventType.APPOINTMENT_CREATED, lambda _: self.refresh_data())
        self.app.events.subscribe(EventType.PATIENT_ARRIVED, lambda _: self.refresh_data())

    def _navigate_to(self, key):
        win = self.window()
        if hasattr(win, "_switch_view"):
            win._switch_view(key)
            if key in win.nav_buttons:
                win.nav_buttons[key].setChecked(True)

    def refresh_data(self):
        self._generate_daily_tasks()
        self._load_tasks()

        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        waiting_count = len(self.app.db.fetch_all("SELECT id FROM appointments WHERE status IN ('CONFIRMED', 'En attente')"))
        vitals_count = len(self.app.db.fetch_all("SELECT id FROM vital_signs WHERE recorded_at >= date('now')"))
        
        self.stats_layout.addWidget(KPICard("Patients en attente", str(waiting_count), "Prise de constantes", "#52c41a"))
        self.stats_layout.addWidget(KPICard("Analyses à valider", "0", "Aucune urgence", "#1890ff"))
        self.stats_layout.addWidget(KPICard("Constantes du jour", str(vitals_count), "Aujourd'hui", "#722ed1"))
        self.stats_layout.addStretch()

    def _generate_daily_tasks(self):
        today = QtCore.QDate.currentDate().toString("yyyy-MM-dd")
        appointments = self.app.db.fetch_all('''
            SELECT a.id, p.first_name, p.last_name, p.id as patient_id
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            WHERE a.scheduled_date = ?
        ''', (today,))
        
        for appt in appointments:
            patient_name = f"{appt['first_name']} {appt['last_name']}"
            patient_id = appt['patient_id']
            
            tasks_to_add = [
                f"Prendre les constantes - {patient_name}",
                f"Préparer salle et matériel pour - {patient_name}"
            ]
            
            for desc in tasks_to_add:
                exists = self.app.db.fetch_one("SELECT id FROM tasks WHERE description = ? AND date_assigned = ?", (desc, today))
                if not exists:
                    self.app.db.execute("INSERT INTO tasks (description, is_completed, patient_id, date_assigned) VALUES (?, 0, ?, ?)",
                                        (desc, patient_id, today))

    def _load_tasks(self):
        self.list_tasks.blockSignals(True)
        self.list_tasks.clear()
        today = QtCore.QDate.currentDate().toString("yyyy-MM-dd")
        
        tasks = self.app.db.fetch_all("SELECT id, description, is_completed FROM tasks WHERE date_assigned = ? ORDER BY is_completed ASC, id DESC", (today,))
        
        for task in tasks:
            item = QtWidgets.QListWidgetItem(task["description"])
            item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.CheckState.Checked if task["is_completed"] else QtCore.Qt.CheckState.Unchecked)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, task["id"])
            
            font = item.font()
            font.setStrikeOut(bool(task["is_completed"]))
            item.setFont(font)
            if task["is_completed"]:
                item.setForeground(QtGui.QBrush(QtGui.QColor("#bfbfbf")))
                
            self.list_tasks.addItem(item)
            
        self.list_tasks.blockSignals(False)

    def _on_task_changed(self, item):
        task_id = item.data(QtCore.Qt.ItemDataRole.UserRole)
        is_completed = 1 if item.checkState() == QtCore.Qt.CheckState.Checked else 0
        self.app.db.execute("UPDATE tasks SET is_completed = ? WHERE id = ?", (is_completed, task_id))
        
        # Step 3: Deduction automatique de stock pour les tâches matérielles
        if is_completed:
            task = self.app.db.get_by_id("tasks", task_id)
            if task and "matériel" in task["description"].lower():
                # On déduit 1 "Gants" ou "Seringues" s'ils existent dans l'inventaire
                self.app.db.execute("UPDATE inventory SET quantity = quantity - 1 WHERE name IN ('Gants', 'Seringues') AND quantity > 0")
        
        font = item.font()
        font.setStrikeOut(bool(is_completed))
        item.setFont(font)
        if is_completed:
            item.setForeground(QtGui.QBrush(QtGui.QColor("#bfbfbf")))
        else:
            item.setForeground(QtGui.QBrush(QtGui.QColor("#141414")))

