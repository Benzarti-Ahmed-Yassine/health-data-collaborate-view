"""
MediERP — Doctor Dashboard View
Design moderne, spacieux et entièrement connecté à la base de données.
"""

from ...utils.qt_compat import QtWidgets, QtCore, QtGui
from ...core.app import SmartMedicalApp


# ─────────────────────────────────────────────
#  Carte KPI agrandie
# ─────────────────────────────────────────────
class _BigKPICard(QtWidgets.QFrame):
    def __init__(self, icon: str, title: str, value: str,
                 sub: str = "", color: str = "#1890ff", parent=None):
        super().__init__(parent)
        self.setObjectName("BigKPICard")
        self.setMinimumHeight(130)
        self.setStyleSheet(f"""
            QFrame#BigKPICard {{
                background-color: white;
                border-radius: 16px;
                border-left: 6px solid {color};
                border-top: 1px solid #e8e8e8;
                border-right: 1px solid #e8e8e8;
                border-bottom: 1px solid #e8e8e8;
            }}
        """)

        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 4)
        shadow.setColor(QtGui.QColor(0, 0, 0, 18))
        self.setGraphicsEffect(shadow)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(18)

        # Icône
        lbl_icon = QtWidgets.QLabel(icon)
        lbl_icon.setStyleSheet(f"font-size: 32pt; color: {color};")
        lbl_icon.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        lbl_icon.setFixedSize(56, 56)
        layout.addWidget(lbl_icon)

        # Textes
        txt = QtWidgets.QVBoxLayout()
        txt.setSpacing(4)

        lbl_title = QtWidgets.QLabel(title)
        lbl_title.setStyleSheet("font-size: 10pt; color: #8c8c8c; font-weight: 500;")
        txt.addWidget(lbl_title)

        self.lbl_value = QtWidgets.QLabel(value)
        self.lbl_value.setStyleSheet(f"font-size: 22pt; font-weight: 800; color: {color};")
        txt.addWidget(self.lbl_value)

        if sub:
            lbl_sub = QtWidgets.QLabel(sub)
            lbl_sub.setStyleSheet("font-size: 9pt; color: #bfbfbf;")
            txt.addWidget(lbl_sub)

        layout.addLayout(txt)
        layout.addStretch()

    def set_value(self, v: str):
        self.lbl_value.setText(v)


# ─────────────────────────────────────────────
#  Carte panneau avec titre
# ─────────────────────────────────────────────
class _Panel(QtWidgets.QFrame):
    def __init__(self, title: str, action_text: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("DashPanel")
        self.setStyleSheet("""
            QFrame#DashPanel {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #e8e8e8;
            }
        """)
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 3)
        shadow.setColor(QtGui.QColor(0, 0, 0, 14))
        self.setGraphicsEffect(shadow)

        self._inner = QtWidgets.QVBoxLayout(self)
        self._inner.setContentsMargins(20, 16, 20, 16)
        self._inner.setSpacing(12)

        # En-tête
        header = QtWidgets.QHBoxLayout()
        lbl = QtWidgets.QLabel(title)
        lbl.setStyleSheet("font-size: 12pt; font-weight: 700; color: #0050b3;")
        header.addWidget(lbl)
        header.addStretch()
        if action_text:
            btn = QtWidgets.QPushButton(action_text)
            btn.setStyleSheet(
                "QPushButton { color: #1890ff; background: transparent; border: none; "
                "font-size: 10pt; font-weight: 600; }"
                "QPushButton:hover { color: #0050b3; }"
            )
            btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            header.addWidget(btn)

        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        sep.setStyleSheet("color: #f0f0f0;")

        self._inner.addLayout(header)
        self._inner.addWidget(sep)

    def body(self) -> QtWidgets.QVBoxLayout:
        return self._inner


# ─────────────────────────────────────────────
#  Item RDV dans la liste
# ─────────────────────────────────────────────
class _RdvItem(QtWidgets.QWidget):
    def __init__(self, time_str, name, status, patient_id, parent=None):
        super().__init__(parent)
        self.patient_id = patient_id
        row = QtWidgets.QHBoxLayout(self)
        row.setContentsMargins(8, 6, 8, 6)
        row.setSpacing(14)

        # Heure
        lbl_h = QtWidgets.QLabel(f"<b>{time_str}</b>")
        lbl_h.setStyleSheet("font-size: 11pt; color: #0050b3; min-width: 50px;")
        row.addWidget(lbl_h)

        # Séparateur vertical
        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        sep.setStyleSheet("color: #d9d9d9;")
        row.addWidget(sep)

        # Nom + motif
        info = QtWidgets.QVBoxLayout()
        info.setSpacing(2)
        lbl_name = QtWidgets.QLabel(f"<b>{name}</b>")
        lbl_name.setStyleSheet("font-size: 11pt; color: #262626;")
        lbl_motif = QtWidgets.QLabel("Consultation générale")
        lbl_motif.setStyleSheet("font-size: 9pt; color: #8c8c8c;")
        info.addWidget(lbl_name)
        info.addWidget(lbl_motif)
        row.addLayout(info)
        row.addStretch()

        # Badge statut
        color_map = {
            "Confirmé":   ("#52c41a", "#f6ffed", "#b7eb8f"),
            "CONFIRMED":  ("#52c41a", "#f6ffed", "#b7eb8f"),
            "En attente": ("#faad14", "#fff7e6", "#ffd591"),
            "Urgent":     ("#ff4d4f", "#fff1f0", "#ffa39e"),
            "COMPLETED":  ("#8c8c8c", "#f5f5f5", "#d9d9d9"),
        }
        fc, bg, bc = color_map.get(status, ("#1890ff", "#e6f7ff", "#91d5ff"))
        badge = QtWidgets.QLabel(status)
        badge.setStyleSheet(
            f"color: {fc}; background-color: {bg}; border: 1px solid {bc};"
            "border-radius: 10px; padding: 3px 10px; font-size: 9pt; font-weight: bold;"
        )
        row.addWidget(badge)


# ─────────────────────────────────────────────
#  Dashboard principal
# ─────────────────────────────────────────────
class DoctorDashboardView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self._last_patient_id = None
        self._setup_ui()

    # ──────────────────────── UI ────────────────────────

    def _setup_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── En-tête utilisateur
        header_frame = QtWidgets.QFrame()
        header_frame.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "stop:0 #1890ff, stop:1 #0050b3);"
        )
        header_frame.setFixedHeight(80)
        header_layout = QtWidgets.QHBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 0, 30, 0)

        user = self.app.current_user or {}
        name = user.get("full_name", "Médecin")
        role = user.get("role", "DOCTOR")
        today_str = QtCore.QDate.currentDate().toString("dddd d MMMM yyyy")

        lbl_hello = QtWidgets.QLabel(f"👨‍⚕️ Bonjour, {name}")
        lbl_hello.setStyleSheet("font-size: 16pt; font-weight: 800; color: white;")
        lbl_date = QtWidgets.QLabel(today_str.capitalize())
        lbl_date.setStyleSheet("font-size: 10pt; color: rgba(255,255,255,0.8);")

        txt_col = QtWidgets.QVBoxLayout()
        txt_col.setSpacing(4)
        txt_col.addWidget(lbl_hello)
        txt_col.addWidget(lbl_date)
        header_layout.addLayout(txt_col)
        header_layout.addStretch()

        self.btn_refresh = QtWidgets.QPushButton("🔄 Actualiser")
        self.btn_refresh.setStyleSheet(
            "QPushButton { background: rgba(255,255,255,0.2); color: white;"
            "border: 1px solid rgba(255,255,255,0.5); border-radius: 8px;"
            "padding: 8px 20px; font-weight: bold; }"
            "QPushButton:hover { background: rgba(255,255,255,0.35); }"
        )
        self.btn_refresh.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.btn_refresh)

        root.addWidget(header_frame)

        # ── Contenu scrollable
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: #f8f9fb;")

        content = QtWidgets.QWidget()
        content.setStyleSheet("background: #f8f9fb;")
        layout = QtWidgets.QVBoxLayout(content)
        layout.setContentsMargins(30, 28, 30, 30)
        layout.setSpacing(24)

        # ── Ligne KPIs
        self.kpi_row = QtWidgets.QHBoxLayout()
        self.kpi_row.setSpacing(20)

        self.kpi_patients = _BigKPICard("👥", "Patients aujourd'hui", "—", color="#1890ff")
        self.kpi_rdv      = _BigKPICard("📅", "Rendez-vous", "—", color="#52c41a")
        self.kpi_revenus  = _BigKPICard("💰", "Revenus générés", "—", color="#722ed1")
        self.kpi_attente  = _BigKPICard("📑", "Factures en attente", "—", color="#fa8c16")

        for kpi in (self.kpi_patients, self.kpi_rdv, self.kpi_revenus, self.kpi_attente):
            self.kpi_row.addWidget(kpi)

        layout.addLayout(self.kpi_row)

        # ── Ligne centrale (2 colonnes larges)
        mid = QtWidgets.QHBoxLayout()
        mid.setSpacing(20)

        # Panneau RDV du jour
        rdv_panel = _Panel("📋 Rendez-vous du jour", "Voir agenda →")
        self.rdv_list = QtWidgets.QListWidget()
        self.rdv_list.setStyleSheet(
            "QListWidget { border: none; background: transparent; outline: none; }"
            "QListWidget::item { border-bottom: 1px solid #f5f5f5; }"
            "QListWidget::item:selected { background: #e6f7ff; border-radius: 8px; }"
            "QListWidget::item:hover { background: #f0f7ff; border-radius: 8px; }"
        )
        self.rdv_list.setMinimumHeight(340)
        self.rdv_list.itemDoubleClicked.connect(self._on_rdv_double_click)
        rdv_panel.body().addWidget(self.rdv_list)
        mid.addWidget(rdv_panel, 3)

        # Panneau droit (dernier patient + actions)
        right_col = QtWidgets.QVBoxLayout()
        right_col.setSpacing(20)

        # Dernier patient
        self.pat_panel = _Panel("👤 Dernier patient vu")
        self.lbl_pat_name = QtWidgets.QLabel("—")
        self.lbl_pat_name.setStyleSheet(
            "font-size: 14pt; font-weight: 800; color: #0050b3;"
        )
        self.lbl_pat_info = QtWidgets.QLabel("Aucun patient consulté aujourd'hui")
        self.lbl_pat_info.setStyleSheet("font-size: 10pt; color: #595959;")
        self.lbl_pat_info.setWordWrap(True)
        self.btn_open_pat = QtWidgets.QPushButton("📁 Ouvrir le dossier")
        self.btn_open_pat.setObjectName("btnPrimary")
        self.btn_open_pat.setFixedHeight(40)
        self.btn_open_pat.hide()
        self.btn_open_pat.clicked.connect(self._open_last_patient)
        self.pat_panel.body().addWidget(self.lbl_pat_name)
        self.pat_panel.body().addWidget(self.lbl_pat_info)
        self.pat_panel.body().addWidget(self.btn_open_pat)
        right_col.addWidget(self.pat_panel)

        # Actions rapides
        act_panel = _Panel("⚡ Actions rapides")
        acts = [
            ("👥", "Mes Patients",    self._go_patients),
            ("📅", "Agenda",          self._go_agenda),
            ("💊", "Ordonnance",      self._go_consultation),
            ("✉️", "Messagerie",      self._go_messages),
        ]
        for icon, label, handler in acts:
            btn = QtWidgets.QPushButton(f"{icon}  {label}")
            btn.setFixedHeight(44)
            btn.setStyleSheet(
                "QPushButton { background: #f0f7ff; color: #0050b3; border: 1px solid #bae0ff;"
                "border-radius: 10px; font-size: 11pt; font-weight: 600; text-align: left; padding-left: 16px; }"
                "QPushButton:hover { background: #bae0ff; border-color: #1890ff; }"
            )
            btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(handler)
            act_panel.body().addWidget(btn)

        right_col.addWidget(act_panel)
        mid.addLayout(right_col, 2)
        layout.addLayout(mid)

        # ── Ligne basse (messages + factures)
        bottom = QtWidgets.QHBoxLayout()
        bottom.setSpacing(20)

        msg_panel = _Panel("✉️ Messages récents", "Voir tout →")
        self.msg_list = QtWidgets.QListWidget()
        self.msg_list.setMinimumHeight(180)
        self.msg_list.setStyleSheet(
            "QListWidget { border: none; background: transparent; outline: none; }"
            "QListWidget::item { padding: 8px 0; border-bottom: 1px solid #f0f0f0; }"
            "QListWidget::item:hover { background: #f0f7ff; border-radius: 6px; }"
        )
        self.msg_list.itemDoubleClicked.connect(self._go_messages)
        msg_panel.body().addWidget(self.msg_list)
        bottom.addWidget(msg_panel, 1)

        fact_panel = _Panel("🧾 Factures récentes")
        self.fact_list = QtWidgets.QListWidget()
        self.fact_list.setMinimumHeight(180)
        self.fact_list.setStyleSheet(
            "QListWidget { border: none; background: transparent; outline: none; }"
            "QListWidget::item { padding: 8px 0; border-bottom: 1px solid #f0f0f0; }"
        )
        fact_panel.body().addWidget(self.fact_list)
        bottom.addWidget(fact_panel, 1)

        layout.addLayout(bottom)

        scroll.setWidget(content)
        root.addWidget(scroll)

        # Timer auto-refresh 30s
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.refresh_data)
        self._timer.start(30000)

        # Abonnements événements
        from ...core.events import EventType
        self.app.events.subscribe(EventType.APPOINTMENT_CREATED,   lambda _: self.refresh_data())
        self.app.events.subscribe(EventType.CONSULTATION_COMPLETED, lambda _: self.refresh_data())
        self.app.events.subscribe(EventType.MESSAGE_SENT,           lambda _: self.refresh_data())

        self.refresh_data()

    # ──────────────────────── DATA ────────────────────────

    def refresh_data(self):
        today = QtCore.QDate.currentDate().toString("yyyy-MM-dd")

        # ── KPIs
        try:
            r = self.app.db.fetch_one(
                "SELECT COUNT(DISTINCT patient_id) as c FROM appointments WHERE DATE(scheduled_date)=?", (today,))
            self.kpi_patients.set_value(str(r['c'] if r else 0))
        except Exception: pass

        try:
            r = self.app.db.fetch_one(
                "SELECT COUNT(id) as c FROM appointments WHERE DATE(scheduled_date)=?", (today,))
            self.kpi_rdv.set_value(str(r['c'] if r else 0))
        except Exception: pass

        try:
            r = self.app.db.fetch_one(
                "SELECT COALESCE(SUM(total_amount),0) as t FROM invoices WHERE status IN ('Payée','Payé')")
            self.kpi_revenus.set_value(f"{r['t']:.0f} DT" if r else "0 DT")
        except Exception: pass

        try:
            r = self.app.db.fetch_one(
                "SELECT COUNT(id) as c FROM invoices WHERE status='En attente'")
            self.kpi_attente.set_value(str(r['c'] if r else 0))
        except Exception: pass

        # ── RDV du jour
        self.rdv_list.clear()
        try:
            rows = self.app.db.fetch_all("""
                SELECT a.id, a.scheduled_date, a.status, a.patient_id,
                       p.first_name || ' ' || p.last_name as full_name
                FROM appointments a
                JOIN patients p ON a.patient_id = p.id
                WHERE DATE(a.scheduled_date) = ?
                ORDER BY a.scheduled_date ASC
            """, (today,))

            if rows:
                for r in rows:
                    t = r['scheduled_date'].split()[-1][:5] if ' ' in r['scheduled_date'] else "—"
                    item = QtWidgets.QListWidgetItem()
                    item.setSizeHint(QtCore.QSize(0, 64))
                    item.setData(QtCore.Qt.ItemDataRole.UserRole, r['patient_id'])
                    widget = _RdvItem(t, r['full_name'], r['status'], r['patient_id'])
                    self.rdv_list.addItem(item)
                    self.rdv_list.setItemWidget(item, widget)
            else:
                empty = QtWidgets.QListWidgetItem("Aucun rendez-vous prévu aujourd'hui.")
                empty.setForeground(QtGui.QBrush(QtGui.QColor("#bfbfbf")))
                self.rdv_list.addItem(empty)
        except Exception as e:
            self.rdv_list.addItem(f"Erreur: {e}")

        # ── Dernier patient vu
        try:
            last = self.app.db.fetch_one("""
                SELECT a.patient_id, p.first_name, p.last_name,
                       p.date_of_birth, p.blood_type, p.phone
                FROM appointments a
                JOIN patients p ON a.patient_id = p.id
                WHERE DATE(a.scheduled_date) = ?
                ORDER BY a.scheduled_date DESC LIMIT 1
            """, (today,))

            if last:
                import datetime as _dt
                age_str = ""
                dob = last.get('date_of_birth', '')
                if dob:
                    try:
                        age = (_dt.date.today() - _dt.datetime.strptime(dob, "%Y-%m-%d").date()).days // 365
                        age_str = f" • {age} ans"
                    except Exception:
                        pass
                self.lbl_pat_name.setText(f"{last['first_name']} {last['last_name']}")
                self.lbl_pat_info.setText(
                    f"Groupe : {last.get('blood_type') or '—'}{age_str}\nTél : {last.get('phone') or '—'}"
                )
                self._last_patient_id = last['patient_id']
                self.btn_open_pat.show()
            else:
                self.lbl_pat_name.setText("—")
                self.lbl_pat_info.setText("Aucun patient consulté aujourd'hui")
                self.btn_open_pat.hide()
                self._last_patient_id = None
        except Exception:
            pass

        # ── Messages récents
        self.msg_list.clear()
        try:
            did = self.app.current_user_id()
            msgs = self.app.db.fetch_all("""
                SELECT m.subject, m.is_read, m.created_at,
                       p.first_name || ' ' || p.last_name as sender
                FROM messages m
                LEFT JOIN patients p ON m.sender_id=p.id AND m.sender_type='PATIENT'
                WHERE m.receiver_id=? AND m.receiver_type='USER'
                ORDER BY m.created_at DESC LIMIT 6
            """, (did,))
            if msgs:
                for m in msgs:
                    prefix = "🔵 " if not m['is_read'] else "   "
                    date = m['created_at'][:10] if m['created_at'] else ""
                    it = QtWidgets.QListWidgetItem(
                        f"{prefix}{m['sender'] or 'Patient'}  —  {m['subject'] or '(sans objet)'}  {date}"
                    )
                    if not m['is_read']:
                        f = it.font(); f.setBold(True); it.setFont(f)
                    self.msg_list.addItem(it)
            else:
                it = QtWidgets.QListWidgetItem("Aucun message.")
                it.setForeground(QtGui.QBrush(QtGui.QColor("#bfbfbf")))
                self.msg_list.addItem(it)
        except Exception:
            pass

        # ── Factures récentes
        self.fact_list.clear()
        try:
            facs = self.app.db.fetch_all("""
                SELECT i.id, i.total_amount, i.status,
                       p.first_name || ' ' || p.last_name as patient
                FROM invoices i
                LEFT JOIN patients p ON i.patient_id=p.id
                ORDER BY i.created_at DESC LIMIT 6
            """)
            color_map = {"Payée": "#52c41a", "Payé": "#52c41a",
                         "En attente": "#faad14", "Annulée": "#ff4d4f"}
            for f in facs:
                it = QtWidgets.QListWidgetItem(
                    f"FACT-{f['id']}  {f['patient'] or '—'}  "
                    f"{f['total_amount']:.2f} DT  {f['status']}"
                )
                color = color_map.get(f['status'], "#595959")
                it.setForeground(QtGui.QBrush(QtGui.QColor(color)))
                self.fact_list.addItem(it)
        except Exception:
            pass

    # ──────────────────────── ACTIONS ────────────────────────

    def _on_rdv_double_click(self, item):
        pid = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if pid:
            win = self.window()
            if hasattr(win, "open_consultation"):
                win.open_consultation(pid)

    def _open_last_patient(self):
        if self._last_patient_id:
            win = self.window()
            if hasattr(win, "open_patient_dossier"):
                win.open_patient_dossier(self._last_patient_id)

    def _navigate_to(self, key):
        win = self.window()
        if hasattr(win, "_switch_view"):
            win._switch_view(key)
            if hasattr(win, "nav_buttons") and key in win.nav_buttons:
                win.nav_buttons[key].setChecked(True)

    def _go_patients(self):    self._navigate_to("patients")
    def _go_agenda(self):      self._navigate_to("agenda")
    def _go_consultation(self): self._navigate_to("consultation")
    def _go_messages(self, *_): self._navigate_to("messages")
