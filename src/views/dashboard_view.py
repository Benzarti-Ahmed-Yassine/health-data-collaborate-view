"""
Smart Medical AI - Dashboard (Senior Edition)
Affichage des RDV avec Photos Patient
"""

from ..utils.qt_compat import QtWidgets, QtCore, QtGui
from ..core.app import SmartMedicalApp
from .components import AvatarLabel

class AppointmentItem(QtWidgets.QWidget):
    """Ligne de rendez-vous avec photo (Style MediERP)"""
    def __init__(self, time, name, reason, status, photo=None):
        super().__init__()
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        self.setObjectName("appointment_item")
        
        lbl_time = QtWidgets.QLabel(time)
        lbl_time.setObjectName("appt_time")
        layout.addWidget(lbl_time)
        
        self.avatar = AvatarLabel(size=35)
        self.avatar.set_photo(photo)
        layout.addWidget(self.avatar)
        
        info_layout = QtWidgets.QVBoxLayout()
        lbl_name = QtWidgets.QLabel(name)
        lbl_name.setObjectName("appt_name")
        lbl_reason = QtWidgets.QLabel(reason)
        lbl_reason.setObjectName("appt_reason")
        info_layout.addWidget(lbl_name)
        info_layout.addWidget(lbl_reason)
        layout.addLayout(info_layout)
        
        layout.addStretch()
        
        lbl_status = QtWidgets.QLabel(status)
        status_colors = {
            "Confirmé": "background-color: #f6ffed; color: #52c41a; border: 1px solid #b7eb8f;",
            "Urgent": "background-color: #fff1f0; color: #ff4d4f; border: 1px solid #ffa39e;",
            "En attente": "background-color: #fff7e6; color: #faad14; border: 1px solid #ffd591;"
        }
        lbl_status.setStyleSheet(status_colors.get(status, "") + "padding: 4px 8px; border-radius: 4px; font-size: 8pt;")
        layout.addWidget(lbl_status)

class StatCard(QtWidgets.QFrame):
    def __init__(self, title, value, subtext, color, icon=""):
        super().__init__()
        self.setObjectName("stat_card")
        self.setFixedSize(300, 150)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header = QtWidgets.QHBoxLayout()
        lbl_title = QtWidgets.QLabel(title)
        lbl_title.setStyleSheet("color: #0050b3; font-size: 10pt;")
        header.addWidget(lbl_title)
        header.addStretch()
        lbl_icon = QtWidgets.QLabel(icon)
        lbl_icon.setStyleSheet(f"font-size: 18pt; color: {color};")
        header.addWidget(lbl_icon)
        layout.addLayout(header)
        
        lbl_value = QtWidgets.QLabel(value)
        lbl_value.setStyleSheet("font-size: 20pt; font-weight: bold; color: #0050b3;")
        layout.addWidget(lbl_value)
        
        lbl_sub = QtWidgets.QLabel(subtext)
        lbl_sub.setStyleSheet(f"color: {color}; font-size: 9pt; font-weight: bold;")
        layout.addWidget(lbl_sub)

class DashboardWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("container")
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(30)

        user_role = self.app.current_user.get('role', 'ASSISTANT') if self.app.current_user else 'ASSISTANT'
        
        # 0. Récupération des données réelles
        today = QtCore.QDate.currentDate().toString("yyyy-MM-dd")
        
        patients_count = len(self.app.db.fetch_all("SELECT id FROM patients WHERE is_active=1"))
        # FIX: Use proper date comparison instead of LIKE to prevent SQL injection
        rdv_count = len(self.app.db.fetch_all("SELECT id FROM appointments WHERE DATE(scheduled_date) = ?", (today,)))
        factures_count = len(self.app.db.fetch_all("SELECT id FROM invoices WHERE status='En attente'"))

        # 1. KPIs dynamiques selon le rôle
        kpi_layout = QtWidgets.QHBoxLayout()
        if user_role == 'DOCTOR':
            kpi_layout.addWidget(StatCard("Total Patients", str(patients_count), "Base active", "#1890ff", "👥"))
            kpi_layout.addWidget(StatCard("RDV Aujourd'hui", str(rdv_count), "Planning", "#52c41a", "📅"))
            kpi_layout.addWidget(StatCard("Revenus (Mois)", "0 €", "En cours", "#722ed1", "💰"))
            kpi_layout.addWidget(StatCard("Factures attente", str(factures_count), "À traiter", "#faad14", "📑"))
        else:
            kpi_layout.addWidget(StatCard("Nouveaux Patients", str(patients_count), "Ce mois", "#1890ff", "👥"))
            kpi_layout.addWidget(StatCard("RDV Aujourd'hui", str(rdv_count), "Accueil", "#52c41a", "📅"))
            kpi_layout.addWidget(StatCard("Factures attente", str(factures_count), "À relancer", "#faad14", "📑"))
            kpi_layout.addWidget(StatCard("Paiements reçus", "0", "Aujourd'hui", "#52c41a", "💳"))
            
        kpi_layout.addStretch()
        main_layout.addLayout(kpi_layout)

        # 2. Main Content
        middle_layout = QtWidgets.QHBoxLayout()
        
        # Left: Prochains RDV
        rdv_panel = QtWidgets.QFrame()
        rdv_panel.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #f0f0f0;")
        rdv_layout = QtWidgets.QVBoxLayout(rdv_panel)
        rdv_layout.addWidget(QtWidgets.QLabel("🕒 Prochains rendez-vous d'aujourd'hui"))
        
        query = """
            SELECT a.scheduled_date, p.first_name, p.last_name, a.status 
            FROM appointments a 
            JOIN patients p ON a.patient_id = p.id
            WHERE DATE(a.scheduled_date) = ?
            ORDER BY a.scheduled_date ASC LIMIT 5
        """
        rdvs = self.app.db.fetch_all(query, (today,))
        if not rdvs:
            rdv_layout.addWidget(QtWidgets.QLabel("Aucun rendez-vous prévu pour aujourd'hui."))
        else:
            for r in rdvs:
                time_str = r['scheduled_date'].split()[-1][:5] if ' ' in r['scheduled_date'] else "00:00"
                rdv_layout.addWidget(AppointmentItem(time_str, f"{r['first_name']} {r['last_name']}", "Consultation", r['status']))
        
        rdv_layout.addStretch()
        middle_layout.addWidget(rdv_panel, 1)
        
        # Right: Empty Placeholder for real Graph later
        graph_panel = QtWidgets.QFrame()
        graph_panel.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #f0f0f0;")
        graph_layout = QtWidgets.QVBoxLayout(graph_panel)
        graph_layout.addWidget(QtWidgets.QLabel("📈 Statistiques des consultations"))
        
        # Real graph will be implemented here
        empty_graph = QtWidgets.QLabel("Pas de données disponibles pour les statistiques actuelles.")
        empty_graph.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        empty_graph.setStyleSheet("color: #0050b3;")
        graph_layout.addWidget(empty_graph, 1)
        
        middle_layout.addWidget(graph_panel, 2)
        
        main_layout.addLayout(middle_layout)
        main_layout.addStretch()

