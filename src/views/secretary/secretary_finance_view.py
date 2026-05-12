"""
MediERP — Secretary Finance View
Gestion des factures clients, achats de matériels et statistiques financières.
"""

from ...utils.qt_compat import QtWidgets, QtCore, QtGui
from ...core.app import SmartMedicalApp
import pyqtgraph as pg
import numpy as np

class SecretaryFinanceView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self._setup_ui()
        self.refresh_data()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # ── Header
        header = QtWidgets.QLabel("Tableau de bord financier")
        header.setStyleSheet("font-size: 22pt; font-weight: bold; color: #1890ff;")
        layout.addWidget(header)

        # ── KPI Cards (Revenue, Expenses, Balance)
        kpi_layout = QtWidgets.QHBoxLayout()
        self.card_revenue = self._create_kpi_card("Chiffre d'Affaires", "0.00 DT", "#1890ff")
        self.card_collected = self._create_kpi_card("Encaissements (Réel)", "0.00 DT", "#52c41a")
        self.card_expenses = self._create_kpi_card("Achats & Matériels", "0.00 DT", "#f5222d")
        kpi_layout.addWidget(self.card_revenue)
        kpi_layout.addWidget(self.card_collected)
        kpi_layout.addWidget(self.card_expenses)
        layout.addLayout(kpi_layout)

        # ── Middle Section: Charts
        charts_panel = QtWidgets.QFrame()
        charts_panel.setStyleSheet("background-color: white; border-radius: 16px; border: 1px solid #f0f0f0;")
        charts_layout = QtWidgets.QVBoxLayout(charts_panel)
        
        lbl_chart = QtWidgets.QLabel("📊 Evolution des Revenus vs Dépenses")
        lbl_chart.setStyleSheet("font-weight: bold; color: #0050b3; font-size: 12pt;")
        charts_layout.addWidget(lbl_chart)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.addLegend()
        charts_layout.addWidget(self.plot_widget)
        
        layout.addWidget(charts_panel, 2)

        # ── Bottom Section: Tabs for Details
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #f0f0f0; border-top: none; background: white; border-radius: 0 0 12px 12px; }
            QTabBar::tab { background: #ffffff; padding: 12px 25px; border: 1px solid #f0f0f0; border-bottom: none; border-radius: 8px 8px 0 0; }
            QTabBar::tab:selected { background: white; font-weight: bold; color: #1890ff; }
        """)

        # Tab 1: Factures Clients
        self.tab_invoices = QtWidgets.QTableWidget()
        self.tab_invoices.setColumnCount(6)
        self.tab_invoices.setHorizontalHeaderLabels(["ID", "Patient", "Total", "Payé", "Reste", "Date"])
        self.tab_invoices.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tabs.addTab(self.tab_invoices, "📑 Factures Clients")
        
        # Tab 1.5: Demandes Matériel (NOUVEAU)
        self.tab_requests = QtWidgets.QTableWidget()
        self.tab_requests.setColumnCount(6)
        self.tab_requests.setHorizontalHeaderLabels(["ID", "Demandeur", "Article", "Qté", "Raison", "Actions"])
        self.tab_requests.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tabs.addTab(self.tab_requests, "🔔 Demandes Matériel")

        # Tab 2: Achats Matériels
        self.tab_purchases = QtWidgets.QTableWidget()
        self.tab_purchases.setColumnCount(6)
        self.tab_purchases.setHorizontalHeaderLabels(["ID", "Article", "Catégorie", "Qté", "Total", "Date"])
        self.tab_purchases.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tabs.addTab(self.tab_purchases, "🛒 Achats Matériels")

        layout.addWidget(self.tabs, 3)

        # ── Actions Footer
        actions_layout = QtWidgets.QHBoxLayout()
        self.btn_new_purchase = QtWidgets.QPushButton("➕ Nouvel Achat")
        self.btn_new_purchase.setStyleSheet("background-color: #f5222d; color: white; border-radius: 8px; padding: 10px 20px; font-weight: bold;")
        self.btn_new_purchase.clicked.connect(self._on_add_purchase)
        
        self.btn_export = QtWidgets.QPushButton("📥 Exporter Rapport (Excel)")
        self.btn_export.setStyleSheet("background-color: #fa8c16; color: white; border-radius: 8px; padding: 10px 20px; font-weight: bold;")
        
        actions_layout.addWidget(self.btn_new_purchase)
        actions_layout.addStretch()
        actions_layout.addWidget(self.btn_export)
        layout.addLayout(actions_layout)

    def _create_kpi_card(self, title, value, color):
        card = QtWidgets.QFrame()
        card.setStyleSheet(f"background-color: white; border-radius: 16px; border: 1px solid #f0f0f0; border-left: 5px solid {color};")
        l = QtWidgets.QVBoxLayout(card)
        t = QtWidgets.QLabel(title)
        t.setStyleSheet("color: #0050b3; font-size: 10pt;")
        v = QtWidgets.QLabel(value)
        v.setObjectName("value")
        v.setStyleSheet(f"color: {color}; font-size: 18pt; font-weight: bold;")
        l.addWidget(t)
        l.addWidget(v)
        return card

    def refresh_data(self):
        try:
            # 1. Factures
            invoices = self.app.db.fetch_all("""
                SELECT i.*, p.first_name || ' ' || p.last_name as patient_name 
                FROM invoices i JOIN patients p ON i.patient_id = p.id 
                ORDER BY i.created_at DESC
            """)
            self.tab_invoices.setRowCount(len(invoices))
            total_turnover = 0
            total_collected = 0
            for i, row in enumerate(invoices):
                total = row['total_amount'] or 0
                paid = row.get('paid_amount', 0) or 0
                rest = total - paid
                
                self.tab_invoices.setItem(i, 0, QtWidgets.QTableWidgetItem(str(row['id'])))
                self.tab_invoices.setItem(i, 1, QtWidgets.QTableWidgetItem(row['patient_name']))
                self.tab_invoices.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{total:.2f} DT"))
                self.tab_invoices.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{paid:.2f} DT"))
                
                rest_item = QtWidgets.QTableWidgetItem(f"{rest:.2f} DT")
                if rest > 0: rest_item.setForeground(QtGui.QColor("#f5222d"))
                self.tab_invoices.setItem(i, 4, rest_item)
                self.tab_invoices.setItem(i, 5, QtWidgets.QTableWidgetItem(row['created_at'][:10]))
                
                total_turnover += total
                total_collected += paid
            
            self.card_revenue.findChild(QtWidgets.QLabel, "value").setText(f"{total_turnover:,.2f} DT")
            self.card_collected.findChild(QtWidgets.QLabel, "value").setText(f"{total_collected:,.2f} DT")

            # 2. Achats
            purchases = self.app.db.fetch_all("SELECT * FROM purchases ORDER BY purchased_at DESC")
            self.tab_purchases.setRowCount(len(purchases))
            total_exp = 0
            for i, row in enumerate(purchases):
                self.tab_purchases.setItem(i, 0, QtWidgets.QTableWidgetItem(str(row['id'])))
                self.tab_purchases.setItem(i, 1, QtWidgets.QTableWidgetItem(row['item_name']))
                self.tab_purchases.setItem(i, 2, QtWidgets.QTableWidgetItem(row['category']))
                self.tab_purchases.setItem(i, 3, QtWidgets.QTableWidgetItem(str(row['quantity'])))
                self.tab_purchases.setItem(i, 4, QtWidgets.QTableWidgetItem(f"{row['total_price']:.2f} DT"))
                self.tab_purchases.setItem(i, 5, QtWidgets.QTableWidgetItem(row['purchased_at'][:10]))
                total_exp += row['total_price']

            self.card_expenses.findChild(QtWidgets.QLabel, "value").setText(f"{total_exp:,.2f} DT")
            
            # 3. Demandes Matériel
            self._load_requests()

            # 4. Graph
            self._update_charts(invoices, purchases)

        except Exception as e:
            print(f"Error refreshing finance data: {e}")

    def _load_requests(self):
        reqs = self.app.db.fetch_all("""
            SELECT r.*, u.full_name as requester_name 
            FROM material_requests r 
            JOIN users u ON r.requester_id = u.id 
            WHERE r.status = 'PENDING'
        """)
        self.tab_requests.setRowCount(len(reqs))
        for i, r in enumerate(reqs):
            self.tab_requests.setItem(i, 0, QtWidgets.QTableWidgetItem(str(r['id'])))
            self.tab_requests.setItem(i, 1, QtWidgets.QTableWidgetItem(r['requester_name']))
            self.tab_requests.setItem(i, 2, QtWidgets.QTableWidgetItem(r['item_name']))
            self.tab_requests.setItem(i, 3, QtWidgets.QTableWidgetItem(str(r['quantity'])))
            self.tab_requests.setItem(i, 4, QtWidgets.QTableWidgetItem(r['reason']))
            
            actions = QtWidgets.QWidget()
            al = QtWidgets.QHBoxLayout(actions)
            al.setContentsMargins(0,0,0,0)
            
            btn_ok = QtWidgets.QPushButton("✅")
            btn_ok.setToolTip("Approuver et passer en achat")
            btn_ok.clicked.connect(lambda checked, rid=r['id']: self._approve_request(rid))
            
            btn_no = QtWidgets.QPushButton("❌")
            btn_no.setToolTip("Rejeter")
            btn_no.clicked.connect(lambda checked, rid=r['id']: self._reject_request(rid))
            
            al.addWidget(btn_ok)
            al.addWidget(btn_no)
            self.tab_requests.setCellWidget(i, 5, actions)

    def _approve_request(self, req_id):
        req = self.app.db.get_by_id("material_requests", req_id)
        if not req: return
        
        # 1. Demander le prix réel
        price, ok = QtWidgets.QInputDialog.getDouble(self, "Validation Achat", f"Prix total pour {req['quantity']} x {req['item_name']} :", 0.0, 0, 100000)
        if not ok: return
        
        # 2. Update request status
        self.app.db.execute("UPDATE material_requests SET status='APPROVED', validator_id=?, validated_at=CURRENT_TIMESTAMP WHERE id=?", (self.app.current_user_id(), req_id))
        
        # 3. Create purchase record
        self.app.db.insert("purchases", {
            "item_name": req["item_name"],
            "category": req["category"],
            "quantity": req["quantity"],
            "total_price": price,
            "unit_price": price / req["quantity"] if req["quantity"] > 0 else price
        })
        
        # 4. Notify & Refresh
        from ...core.events import EventType
        self.app.events.emit(EventType.MATERIAL_APPROVED, req_id)
        self.refresh_data()
        QtWidgets.QMessageBox.information(self, "Succès", "Demande approuvée et ajoutée au bilan financier.")

    def _reject_request(self, req_id):
        self.app.db.execute("UPDATE material_requests SET status='REJECTED', validator_id=?, validated_at=CURRENT_TIMESTAMP WHERE id=?", (self.app.current_user_id(), req_id))
        self.refresh_data()

    def search(self, text):
        """Recherche globale dans les factures et achats."""
        text = text.lower()
        # Filtre invoices
        for row in range(self.tab_invoices.rowCount()):
            match = False
            for col in range(self.tab_invoices.columnCount()):
                item = self.tab_invoices.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            self.tab_invoices.setRowHidden(row, not match)

    def _update_charts(self, invoices, purchases):
        self.plot_widget.clear()
        
        # Simulation de données temporelles sur les 30 derniers jours
        days = np.arange(30)
        rev_data = np.zeros(30)
        exp_data = np.zeros(30)
        
        # Remplissage simplifié pour la démo
        rev_data = np.cumsum(np.random.randint(50, 200, 30))
        exp_data = np.cumsum(np.random.randint(20, 100, 30))

        self.plot_widget.plot(days, rev_data, pen=pg.mkPen('#52c41a', width=3), name="Revenus (Cumul)")
        self.plot_widget.plot(days, exp_data, pen=pg.mkPen('#f5222d', width=3), name="Dépenses (Cumul)")

    def _on_add_purchase(self):
        # Dialog simple pour ajouter un achat
        name, ok1 = QtWidgets.QInputDialog.getText(self, "Nouvel Achat", "Nom de l'article :")
        if ok1 and name:
            price, ok2 = QtWidgets.QInputDialog.getDouble(self, "Prix", "Montant Total (DT) :", 10.0, 0, 100000)
            if ok2:
                self.app.db.insert("purchases", {
                    "item_name": name,
                    "category": "MATERIAL",
                    "quantity": 1,
                    "unit_price": price,
                    "total_price": price
                })
                self.refresh_data()
                QtWidgets.QMessageBox.information(self, "Succès", "Achat enregistré.")
