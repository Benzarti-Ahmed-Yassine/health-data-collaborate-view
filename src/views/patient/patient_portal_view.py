from ...utils.qt_compat import QtWidgets, QtCore, QtGui
from ...core.app import SmartMedicalApp
from ..components import KPICard

class PatientPortalView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self.user = self.app.current_user
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground)

        # Welcome
        header = QtWidgets.QLabel(f"👋 Bienvenue sur votre portail, {self.user.get('full_name')}")
        header.setProperty("class", "header_text")
        layout.addWidget(header)

        # Quick Stats
        self.stats_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(self.stats_layout)

        # Information Panels
        panels = QtWidgets.QHBoxLayout()
        
        # Documents
        docs = QtWidgets.QFrame()
        docs.setProperty("class", "card")
        doc_layout = QtWidgets.QVBoxLayout(docs)
        
        doc_title = QtWidgets.QLabel("📂 Mes Documents Récents")
        doc_title.setProperty("class", "section_title")
        doc_layout.addWidget(doc_title)
        
        self.list_docs = QtWidgets.QListWidget()
        self.list_docs.setObjectName("portal_list")
        doc_layout.addWidget(self.list_docs)
        
        panels.addWidget(docs, 2)
        
        # Actions
        actions = QtWidgets.QFrame()
        actions.setFixedWidth(320)
        actions.setObjectName("patient_card_warning")
        act_layout = QtWidgets.QVBoxLayout(actions)
        
        act_title = QtWidgets.QLabel("✨ Services Rapides")
        act_title.setProperty("class", "section_title")
        act_layout.addWidget(act_title)
        
        self.btn_rdv = QtWidgets.QPushButton("📅 Prendre RDV")
        self.btn_msg = QtWidgets.QPushButton("✉️ Écrire au Docteur")
        self.btn_prof = QtWidgets.QPushButton("👤 Mon Profil")
        
        for b in [self.btn_rdv, self.btn_msg, self.btn_prof]:
            b.setFixedHeight(50)
            b.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            b.setObjectName("btnPatientAction")
            act_layout.addWidget(b)
            
        self.btn_rdv.clicked.connect(lambda: self._navigate_to("pat_appointments"))
        self.btn_msg.clicked.connect(lambda: self._navigate_to("pat_messages"))
        self.btn_prof.clicked.connect(lambda: self._navigate_to("pat_profile"))

        act_layout.addStretch()
        panels.addWidget(actions, 1)
        
        layout.addLayout(panels)
        layout.addStretch()

        self.refresh_data()

    def _navigate_to(self, key):
        win = self.window()
        if hasattr(win, "_switch_view"):
            win._switch_view(key)
            if key in win.nav_buttons:
                win.nav_buttons[key].setChecked(True)

    def refresh_data(self):
        try:
            pid = self.app.current_user_id()
            
            # Clear stats
            while self.stats_layout.count():
                item = self.stats_layout.takeAt(0)
                if item.widget(): item.widget().deleteLater()

            # Next RDV
            query_rdv = "SELECT scheduled_date FROM appointments WHERE patient_id = ? AND scheduled_date >= date('now') ORDER BY scheduled_date ASC LIMIT 1"
            next_rdv = self.app.db.fetch_one(query_rdv, (pid,))
            rdv_txt = next_rdv['scheduled_date'] if next_rdv else "Aucun RDV"
            rdv_sub = "Consultation à venir" if next_rdv else "Prenez rendez-vous"

            # Prescriptions
            count_presc = len(self.app.db.fetch_all("SELECT id FROM prescriptions WHERE patient_id = ?", (pid,)))
            
            # Messages
            count_msg = len(self.app.db.fetch_all("SELECT id FROM messages WHERE receiver_id = ? AND is_read = 0", (pid,)))

            self.stats_layout.addWidget(KPICard("Prochain RDV", rdv_txt, rdv_sub, "#fa8c16"))
            self.stats_layout.addWidget(KPICard("Ordonnances", str(count_presc), "Historique complet", "#52c41a"))
            self.stats_layout.addWidget(KPICard("Messages", str(count_msg), "Nouveaux messages", "#1890ff"))
            self.stats_layout.addStretch()

            # Documents
            self.list_docs.clear()
            docs = self.app.db.fetch_all("SELECT file_path, created_at FROM medical_documents WHERE patient_id = ? LIMIT 5", (pid,))
            for d in docs:
                self.list_docs.addItem(f"📄 {d['file_path']} ({d['created_at'][:10]})")
            if not docs:
                self.list_docs.addItem("Aucun document disponible.")

        except Exception as e:
            print(f"Error refreshing portal: {e}")

