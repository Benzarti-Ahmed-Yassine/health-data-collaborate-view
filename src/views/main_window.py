"""
Smart Medical AI — MainWindow (Antigravity RBAC Edition)
Navigation dynamique selon les 5 rôles : ADMIN, DOCTOR, SECRETARY, ASSISTANT, PATIENT
"""

from ..utils.qt_compat import QtWidgets, QtCore, QtGui
from .components import AvatarLabel
from ..core.app import SmartMedicalApp


# ─── Menu definitions per role ────────────────────────────────────────────────

ROLE_MENUS = {
    "ADMIN": [
        ("admin_dashboard", "🛡️ Administration"),
        ("admin_users",     "👥 Utilisateurs"),
        ("admin_settings",  "⚙️ Paramètres"),
        ("admin_audit",     "🔍 Audit & Conformité"),
    ],
    "DOCTOR": [
        ("dashboard",    "📊 Tableau de bord"),
        ("patients",     "👥 Mes Patients"),
        ("agenda",       "📅 Agenda"),
        ("consultation", "🩺 Consultation IA"),
        ("doctor_prescriptions", "💊 Ordonnances"),
        ("messages",     "✉️ Messagerie"),
    ],
    "SECRETARY": [
        ("sec_dashboard", "📊 Tableau de bord"),
        ("patients",      "👥 Mes Patients"),
        ("sec_agenda",    "📅 Calendrier Clinique"),
        ("sec_finance",   "💰 Finances & Achats"),
        ("sec_billing",   "💰 Facturation"),
    ],
    "ASSISTANT": [
        ("asst_dashboard", "📊 Tableau de bord"),
        ("asst_patients",  "👥 Mes Patients"),
        ("asst_vitals",    "📋 Constantes Vitales"),
        ("asst_inventory", "📦 Stocks & Vaccins"),
    ],
    "PATIENT": [
        ("pat_dashboard",       "🏠 Mon Portail"),
        ("pat_appointments",    "📅 Mes Rendez-vous"),
        ("pat_prescriptions",   "💊 Mes Ordonnances"),
        ("pat_messages",        "✉️ Messages"),
        ("pat_profile",         "👤 Mon Profil"),
    ],
}

ROLE_COLORS = {
    "ADMIN":     "#722ed1",
    "DOCTOR":    "#1890ff",
    "SECRETARY": "#13c2c2",
    "ASSISTANT": "#52c41a",
    "PATIENT":   "#fa8c16",
}

ROLE_LABELS = {
    "ADMIN":     "Administrateur",
    "DOCTOR":    "Médecin",
    "SECRETARY": "Secrétaire",
    "ASSISTANT": "Assistant Médical",
    "PATIENT":   "Patient",
}


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.app = SmartMedicalApp.get_instance()
        self.user_data = self.app.current_user or {}
        self.role = self.user_data.get("role", "DOCTOR")
        self._role_color = ROLE_COLORS.get(self.role, "#1890ff")

        self.views = {}
        self.nav_buttons = {}

        self._setup_ui()
        self._load_views()
        self._connect_signals()
        self._select_first_menu()

    # ================================================================
    # UI SETUP
    # ================================================================

    def _setup_ui(self):
        self.setWindowTitle("MediERP — Système de Gestion Médicale")
        self.setMinimumSize(1400, 900)

        central = QtWidgets.QWidget()
        central.setObjectName("central_widget")
        self.setCentralWidget(central)
        root = QtWidgets.QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar
        sidebar = self._build_sidebar()
        root.addWidget(sidebar)

        # 🏥 Content area
        content_area = QtWidgets.QWidget()
        content_area.setObjectName("content_area_container")
        content_layout = QtWidgets.QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        header = self._build_header()
        content_layout.addWidget(header)

        self.stack = QtWidgets.QStackedWidget()
        self.stack.setObjectName("content_area")
        content_layout.addWidget(self.stack)

        root.addWidget(content_area)

    def _build_sidebar(self) -> QtWidgets.QFrame:
        sidebar = QtWidgets.QFrame()
        sidebar.setObjectName("nav_panel")
        sidebar.setFixedWidth(265)

        layout = QtWidgets.QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo
        logo_frame = QtWidgets.QFrame()
        logo_frame.setFixedHeight(72)
        logo_frame.setObjectName("logo_frame")
        logo_layout = QtWidgets.QHBoxLayout(logo_frame)
        logo_layout.setContentsMargins(20, 0, 20, 0)

        ico = QtWidgets.QLabel("➕")
        ico.setObjectName("logo_icon")
        name_lbl = QtWidgets.QLabel("MediERP")
        name_lbl.setObjectName("logo_name")
        logo_layout.addWidget(ico)
        logo_layout.addWidget(name_lbl)
        logo_layout.addStretch()
        layout.addWidget(logo_frame)

        # Role badge
        badge = QtWidgets.QLabel(f"  {ROLE_LABELS.get(self.role, self.role)}")
        badge.setFixedHeight(32)
        badge.setObjectName("role_badge")
        layout.addWidget(badge)

        layout.addSpacing(8)

        # Navigation buttons
        self.btn_group = QtWidgets.QButtonGroup(self)
        menus = ROLE_MENUS.get(self.role, ROLE_MENUS["DOCTOR"])

        for key, label in menus:
            btn = self._make_nav_button(label)
            self.btn_group.addButton(btn)
            self.nav_buttons[key] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # Logout button
        btn_logout = QtWidgets.QPushButton("🚪  Déconnexion")
        btn_logout.setFixedHeight(48)
        btn_logout.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        btn_logout.setObjectName("btnLogout")
        btn_logout.clicked.connect(self._on_logout)
        layout.addWidget(btn_logout)

        # Profile card
        profile = self._build_profile_card()
        layout.addWidget(profile)

        return sidebar

    def _make_nav_button(self, label: str) -> QtWidgets.QPushButton:
        btn = QtWidgets.QPushButton(f"  {label}")
        btn.setCheckable(True)
        btn.setFixedHeight(52)
        btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        btn.setProperty("nav_button", True)
        btn.setObjectName("nav_button")
        return btn

    def _build_header(self) -> QtWidgets.QFrame:
        header = QtWidgets.QFrame()
        header.setObjectName("header_bar")
        header.setFixedHeight(72)
        layout = QtWidgets.QHBoxLayout(header)
        layout.setContentsMargins(30, 0, 30, 0)

        name = self.user_data.get("full_name", "Utilisateur").split()[-1]
        self.lbl_welcome = QtWidgets.QLabel(f"Bonjour, {name} 👋")
        self.lbl_welcome.setObjectName("lbl_welcome")
        layout.addWidget(self.lbl_welcome)
        layout.addStretch()

        # Search bar
        search = QtWidgets.QLineEdit()
        search.setPlaceholderText("🔍  Rechercher (Nom ou Date)...")
        search.setFixedWidth(280)
        search.setFixedHeight(38)
        search.setObjectName("main_search")
        search.textChanged.connect(self._on_search)
        layout.addWidget(search)

        return header

    def _build_profile_card(self) -> QtWidgets.QFrame:
        card = QtWidgets.QFrame()
        card.setObjectName("profile_card")
        card.setFixedHeight(70)
        layout = QtWidgets.QHBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)

        avatar = AvatarLabel(size=38)
        avatar.set_photo(self.user_data.get("photo_path"))
        layout.addWidget(avatar)

        info = QtWidgets.QVBoxLayout()
        lbl_name = QtWidgets.QLabel(self.user_data.get("full_name", "Utilisateur"))
        lbl_name.setObjectName("profile_name")
        lbl_role = QtWidgets.QLabel(ROLE_LABELS.get(self.role, self.role))
        lbl_role.setObjectName("profile_role")
        info.addWidget(lbl_name)
        info.addWidget(lbl_role)
        layout.addLayout(info)
        layout.addStretch()

        return card

    # ================================================================
    # VIEW LOADING (lazy by role)
    # ================================================================

    def _load_views(self):
        """Charge les vues correspondant au rôle actuel."""
        if self.role == "ADMIN":
            self._load_admin_views()
        elif self.role == "DOCTOR":
            self._load_doctor_views()
        elif self.role == "SECRETARY":
            self._load_secretary_views()
        elif self.role == "ASSISTANT":
            self._load_assistant_views()
        elif self.role == "PATIENT":
            self._load_patient_views()
        else:
            self._load_doctor_views()  # fallback

        for view in self.views.values():
            self.stack.addWidget(view)

    def _load_admin_views(self):
        from .admin.admin_dashboard_view import AdminDashboardView
        from .admin.user_management_view import UserManagementView
        from .admin.system_settings_view import SystemSettingsView
        from .admin.audit_view import AuditView
        self.views = {
            "admin_dashboard": AdminDashboardView(),
            "admin_users":     UserManagementView(),
            "admin_settings":  SystemSettingsView(),
            "admin_audit":     AuditView(),
        }

    def _load_doctor_views(self):
        from .doctor.doctor_dashboard_view import DoctorDashboardView
        from .patient_view import PatientListView
        from .patient_detail_view import PatientDetailView
        from .consultation_view import ConsultationWidget
        from .doctor.doctor_agenda_view import DoctorAgendaView
        from .doctor.doctor_messages_view import DoctorMessagesView
        from .doctor.doctor_prescriptions_view import DoctorPrescriptionsView
        from .extra_views import FacturationWidget
        self.views = {
            "dashboard":    DoctorDashboardView(),
            "patients":     PatientListView(),
            "patient_detail": PatientDetailView(),
            "agenda":       DoctorAgendaView(),
            "consultation": ConsultationWidget(),
            "doctor_prescriptions": DoctorPrescriptionsView(),
            "messages":     DoctorMessagesView(),
            "billing":      FacturationWidget(),
        }

    def _load_secretary_views(self):
        from .secretary.secretary_dashboard_view import SecretaryDashboardView
        from .secretary.secretary_agenda_view import SecretaryAgendaView
        from .secretary.secretary_billing_view import SecretaryBillingView
        from .secretary.secretary_finance_view import SecretaryFinanceView
        from .patient_view import PatientListView
        from .patient_detail_view import PatientDetailView
        self.views = {
            "sec_dashboard": SecretaryDashboardView(),
            "patients":      PatientListView(),
            "patient_detail": PatientDetailView(),
            "sec_agenda":    SecretaryAgendaView(),
            "sec_finance":   SecretaryFinanceView(),
            "sec_billing":   SecretaryBillingView(),
        }

    def _load_assistant_views(self):
        from .assistant.assistant_dashboard_view import AssistantDashboardView
        from .assistant.assistant_patients_view import AssistantPatientsView
        from .assistant.vital_signs_view import VitalSignsView
        from .assistant.assistant_inventory_view import AssistantInventoryView
        self.views = {
            "asst_dashboard": AssistantDashboardView(),
            "asst_patients":  AssistantPatientsView(),
            "asst_vitals":    VitalSignsView(),
            "asst_inventory": AssistantInventoryView(),
        }

    def _load_patient_views(self):
        from .patient.patient_portal_view import PatientPortalView
        from .patient.patient_appointments_view import PatientAppointmentsView
        from .patient.patient_prescriptions_view import PatientPrescriptionsView
        from .patient.patient_messages_view import PatientMessagesView
        from .patient.patient_profile_view import PatientProfileView
        self.views = {
            "pat_dashboard":     PatientPortalView(),
            "pat_appointments":  PatientAppointmentsView(),
            "pat_prescriptions": PatientPrescriptionsView(),
            "pat_messages":      PatientMessagesView(),
            "pat_profile":       PatientProfileView(),
        }

    # ================================================================
    # NAVIGATION
    # ================================================================

    def _connect_signals(self):
        for key, btn in self.nav_buttons.items():
            btn.clicked.connect(lambda checked, k=key: self._switch_view(k))

    def _switch_view(self, key: str):
        if key in self.views:
            target_view = self.views[key]
            self.stack.setCurrentWidget(target_view)
            
            # Animation de fondu
            eff = QtWidgets.QGraphicsOpacityEffect(target_view)
            target_view.setGraphicsEffect(eff)
            
            anim = QtCore.QPropertyAnimation(eff, b"opacity")
            anim.setDuration(400)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QtCore.QEasingCurve.Type.OutQuad)
            
            # Nettoyage de l'effet après l'animation pour éviter les conflits de QPainter
            anim.finished.connect(lambda: target_view.setGraphicsEffect(None))
            
            anim.start(QtCore.QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            self.fade_anim_ref = anim # garder ref active

    def _on_search(self, text):
        """Délègue la recherche à la vue active si elle supporte la méthode search()."""
        current_view = self.stack.currentWidget()
        if hasattr(current_view, "search"):
            current_view.search(text)

    def _select_first_menu(self):
        """Sélectionne le premier menu et affiche la première vue."""
        if self.nav_buttons:
            first_key = next(iter(self.nav_buttons))
            self.nav_buttons[first_key].setChecked(True)
            self._switch_view(first_key)

    # ================================================================
    # ACTIONS
    # ================================================================

    def open_patient_dossier(self, patient_id: int):
        """Ouvre le dossier détaillé d'un patient (vue Doctor)."""
        if "patient_detail" in self.views:
            detail = self.views["patient_detail"]
            detail.load_patient(patient_id)
            self.stack.setCurrentWidget(detail)
            if "patients" in self.nav_buttons:
                self.nav_buttons["patients"].setChecked(True)

    def open_consultation(self, patient_id: int):
        """Ouvre la vue consultation avec un patient actif."""
        if "consultation" in self.views:
            consult = self.views["consultation"]
            if hasattr(consult, "load_patient"):
                consult.load_patient(patient_id)
            self.stack.setCurrentWidget(consult)
            if "consultation" in self.nav_buttons:
                self.nav_buttons["consultation"].setChecked(True)

    def _on_logout(self):
        reply = QtWidgets.QMessageBox.question(
            self, "Déconnexion",
            "Voulez-vous vraiment vous déconnecter ?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.app.logout()
            self.close()
