"""
Smart Medical AI - Additional Views
Classes pour Agenda, Facturation, Admin, etc. (Compatible Multi-Qt)
"""

import os
from ..utils.qt_compat import QtWidgets, QtCore, uic

class GenericUiWidget(QtWidgets.QWidget):
    """Classe générique pour charger un fichier .ui"""
    def __init__(self, ui_filename, parent=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(__file__), "ui", ui_filename)
        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)

class AgendaWidget(GenericUiWidget):
    def __init__(self, parent=None):
        super().__init__("agenda.ui", parent)

class FacturationWidget(GenericUiWidget):
    def __init__(self, parent=None):
        super().__init__("facturation.ui", parent)

from ..core.app import SmartMedicalApp
from .dashboard_view import StatCard

class AdminDashboardWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(30)

        # SQL Data Fetching
        users_count = len(self.app.db.fetch_all("SELECT id FROM users"))
        doctors_count = len(self.app.db.fetch_all("SELECT id FROM users WHERE role='DOCTOR'"))
        assistants_count = len(self.app.db.fetch_all("SELECT id FROM users WHERE role='ASSISTANT'"))
        patients_count = len(self.app.db.fetch_all("SELECT id FROM patients"))

        # 1. KPIs
        kpi_layout = QtWidgets.QHBoxLayout()
        kpi_layout.addWidget(StatCard("Utilisateurs", str(users_count), "Système", "#1890ff", "👤"))
        kpi_layout.addWidget(StatCard("Médecins", str(doctors_count), "Actifs", "#52c41a", "👨‍⚕️"))
        kpi_layout.addWidget(StatCard("Secrétaires", str(assistants_count), "Actifs", "#722ed1", "👩‍💼"))
        kpi_layout.addWidget(StatCard("Patients", str(patients_count), "Total", "#faad14", "👥"))
        kpi_layout.addStretch()
        main_layout.addLayout(kpi_layout)

        # 2. Main Content
        middle_layout = QtWidgets.QHBoxLayout()
        
        # Left: Graph
        graph_panel = QtWidgets.QFrame()
        graph_panel.setObjectName("panel_white")
        graph_layout = QtWidgets.QVBoxLayout(graph_panel)
        graph_layout.addWidget(QtWidgets.QLabel("📈 Activité des utilisateurs (30 derniers jours)"))
        mock_graph = QtWidgets.QLabel()
        mock_graph = QtWidgets.QLabel()
        mock_graph.setObjectName("mock_graph")
        graph_layout.addWidget(mock_graph, 1)
        middle_layout.addWidget(graph_panel, 2)
        
        # Right: Roles Pie Chart
        pie_panel = QtWidgets.QFrame()
        pie_panel.setObjectName("panel_white")
        pie_layout = QtWidgets.QVBoxLayout(pie_panel)
        pie_layout.addWidget(QtWidgets.QLabel("📊 Utilisation des rôles"))
        mock_pie = QtWidgets.QLabel("🔵 Médecins 🔴 Secrétaires 🟡 Admin")
        mock_pie.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        pie_layout.addWidget(mock_pie, 1)
        middle_layout.addWidget(pie_panel, 1)
        
        main_layout.addLayout(middle_layout)
        main_layout.addStretch()

class UserManagementWidget(GenericUiWidget):
    def __init__(self, parent=None):
        super().__init__("user_management.ui", parent)

class SettingsWidget(GenericUiWidget):
    def __init__(self, parent=None):
        super().__init__("settings.ui", parent)
