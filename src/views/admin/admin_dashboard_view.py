"""
MediERP — Admin Dashboard View
Console d'administration avec rafraîchissement automatique.
"""

from ...utils.qt_compat import QtWidgets, QtCore, QtGui
from ...core.app import SmartMedicalApp
from ..components import KPICard


class AdminDashboardView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self._setup_ui()
        self.refresh_data()

        # Rafraîchissement toutes les 30 secondes
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(30_000)

        # Abonnements EventBus
        from ...core.events import EventType
        self.app.events.subscribe(EventType.USER_LOGIN,   lambda _: self.refresh_data())
        self.app.events.subscribe(EventType.USER_LOGOUT,  lambda _: self.refresh_data())
        self.app.events.subscribe(EventType.PATIENT_CREATED, lambda _: self.refresh_data())

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # Header
        header_row = QtWidgets.QHBoxLayout()
        header = QtWidgets.QLabel("🛡️ Console d'Administration Système")
        header.setObjectName("header_title")
        header_row.addWidget(header)
        header_row.addStretch()

        btn_refresh = QtWidgets.QPushButton("🔄 Actualiser")
        btn_refresh.setFixedHeight(36)
        btn_refresh.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        btn_refresh.setObjectName("btnSecondary")
        btn_refresh.clicked.connect(self.refresh_data)
        header_row.addWidget(btn_refresh)
        layout.addLayout(header_row)

        # KPI Grid
        self.kpi_layout = QtWidgets.QHBoxLayout()
        self.kpi_layout.setSpacing(20)
        layout.addLayout(self.kpi_layout)

        # Audit Preview Table
        audit_header = QtWidgets.QHBoxLayout()
        audit_header.addWidget(QtWidgets.QLabel(
            "<b>🔍 Derniers événements de sécurité (Audit Trail)</b>"
        ))
        audit_header.addStretch()
        layout.addLayout(audit_header)

        self.table = QtWidgets.QTableWidget(5, 5)
        self.table.setHorizontalHeaderLabels(["Date", "Utilisateur", "Action", "Ressource", "Hash"])
        self.table.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setObjectName("admin_table")
        layout.addWidget(self.table)
        layout.addStretch()

    def refresh_data(self):
        # Vider KPI
        while self.kpi_layout.count():
            item = self.kpi_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Données réelles
        try:
            users_count  = len(self.app.db.fetch_all("SELECT id FROM users"))
            audit_count  = len(self.app.db.fetch_all("SELECT id FROM audit_logs"))
            roles_count  = len(self.app.db.fetch_all("SELECT id FROM roles"))
            patients_count = len(self.app.db.fetch_all("SELECT id FROM patients WHERE is_active = 1"))

            self.kpi_layout.addWidget(KPICard("Utilisateurs",    str(users_count),    "Comptes actifs",          "#722ed1", "👤"))
            self.kpi_layout.addWidget(KPICard("Patients",         str(patients_count), "Dossiers actifs",         "#1890ff", "🏥"))
            self.kpi_layout.addWidget(KPICard("Logs d'Audit",    str(audit_count),    "Événements sécurisés",    "#52c41a", "🔒"))
            self.kpi_layout.addWidget(KPICard("Rôles RBAC",      str(roles_count),    "Niveaux de permission",   "#faad14", "🛡️"))
            self.kpi_layout.addStretch()

            # Peupler le tableau d'audit
            logs = self.app.db.fetch_all(
                "SELECT timestamp, user_id, action, table_name, current_hash FROM audit_logs ORDER BY id DESC LIMIT 5"
            )
            self.table.setRowCount(max(len(logs), 1))
            for i, log in enumerate(logs):
                self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(log['timestamp'])[:19]))
                self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(log['user_id'])))
                self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(log['action']))
                self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(log['table_name'] or "Système"))
                hash_abbr = (log['current_hash'] or "")[:12] + "..."
                self.table.setItem(i, 4, QtWidgets.QTableWidgetItem(hash_abbr))

            if not logs:
                self.table.setRowCount(1)
                self.table.setSpan(0, 0, 1, 5)
                self.table.setItem(0, 0, QtWidgets.QTableWidgetItem("Aucun événement d'audit enregistré."))

        except Exception as e:
            print(f"[AdminDashboard] Erreur refresh: {e}")
