from ...utils.qt_compat import QtWidgets, QtCore, QtGui
from ...core.app import SmartMedicalApp

class SecretaryBillingView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header = QtWidgets.QLabel("💰 Facturation & Paiements")
        header.setStyleSheet("font-size: 20pt; font-weight: bold; color: #13c2c2;")
        layout.addWidget(header)

        # Actions
        actions_layout = QtWidgets.QHBoxLayout()
        actions_layout.addStretch()
        self.btn_new_invoice = QtWidgets.QPushButton("💰 Créer Facture")
        self.btn_new_invoice.setStyleSheet("background-color: #13c2c2; color: white; font-weight: bold; padding: 8px 15px; border-radius: 6px;")
        self.btn_new_invoice.clicked.connect(self._on_new_invoice)
        actions_layout.addWidget(self.btn_new_invoice)
        layout.addLayout(actions_layout)

        # Invoices Table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Facture #", "Patient", "Total", "Payé", "Reste", "Statut", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("background-color: white; border-radius: 8px;")
        layout.addWidget(self.table)

        self._load_invoices()

        # Temps Réel
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._load_invoices)
        self.timer.start(15000) # Rafraîchir toutes les 15s

        from ...core.events import EventType
        self.app.events.subscribe(EventType.INVOICE_CREATED, lambda _: self._load_invoices())
        self.app.events.subscribe(EventType.INVOICE_UPDATED, lambda _: self._load_invoices())

    def _load_invoices(self):
        try:
            query = """
                SELECT i.id, p.first_name, p.last_name, i.total_amount, i.created_at, i.status
                FROM invoices i
                JOIN patients p ON i.patient_id = p.id
                ORDER BY i.created_at DESC
            """
            invoices = self.app.db.fetch_all(query)
            self.table.setRowCount(len(invoices))
            for i, inv in enumerate(invoices):
                total = inv['total_amount'] or 0
                paid = inv.get('paid_amount', 0) or 0
                rest = total - paid
                
                self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(f"INV-{inv['id']:04d}"))
                self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(f"{inv['first_name']} {inv['last_name']}"))
                self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{total:.2f} DT"))
                self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{paid:.2f} DT"))
                
                rest_item = QtWidgets.QTableWidgetItem(f"{rest:.2f} DT")
                if rest > 0:
                    rest_item.setForeground(QtGui.QColor("#ff4d4f"))
                self.table.setItem(i, 4, rest_item)
                
                status_item = QtWidgets.QTableWidgetItem(inv['status'])
                color = "#52c41a" if inv['status'] == 'Payé' else "#faad14"
                status_item.setForeground(QtGui.QColor(color))
                self.table.setItem(i, 5, status_item)
                
                # Actions
                actions = QtWidgets.QWidget()
                al = QtWidgets.QHBoxLayout(actions)
                al.setContentsMargins(0, 0, 0, 0)
                
                btn_edit = QtWidgets.QPushButton("✏️")
                btn_edit.setFixedWidth(30)
                btn_edit.clicked.connect(lambda checked, iid=inv['id']: self._on_edit_invoice(iid))
                al.addWidget(btn_edit)
                
                btn_del = QtWidgets.QPushButton("🗑️")
                btn_del.setFixedWidth(30)
                btn_del.clicked.connect(lambda checked, iid=inv['id']: self._on_delete_invoice(iid))
                al.addWidget(btn_del)
                
                self.table.setCellWidget(i, 6, actions)
                
        except Exception as e:
            print(f"Error loading invoices: {e}")

    def search(self, text):
        """Recherche globale dans les factures."""
        text = text.lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def _on_new_invoice(self):
        from .secretary_billing_view import InvoiceDialog
        from ...core.events import EventType
        dialog = InvoiceDialog(self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if self.app.db.insert("invoices", data):
                self.app.events.emit(EventType.INVOICE_CREATED, data)
                QtWidgets.QMessageBox.information(self, "Succès", "Facture créée.")
                self._load_invoices()

    def _on_edit_invoice(self, iid):
        from ...core.events import EventType
        inv_data = self.app.db.get_by_id("invoices", iid)
        if not inv_data: return
        dialog = InvoiceDialog(self, inv_data)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if self.app.db.update("invoices", iid, data):
                self.app.events.emit(EventType.INVOICE_UPDATED, data)
                self._load_invoices()

    def _on_delete_invoice(self, iid):
        from ...core.events import EventType
        if QtWidgets.QMessageBox.question(self, "Confirmer", "Supprimer cette facture ?") == QtWidgets.QMessageBox.StandardButton.Yes:
            if self.app.db.delete("invoices", iid):
                self.app.events.emit(EventType.INVOICE_UPDATED, {"id": iid, "action": "delete"})
                self._load_invoices()

class InvoiceDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, inv_data=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self.inv_data = inv_data
        self.setWindowTitle("Modifier la Facture" if inv_data else "Nouvelle Facture")
        self.setFixedWidth(350)
        self._setup_ui()

    def _setup_ui(self):
        l = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        
        self.cb_patient = QtWidgets.QComboBox()
        patients = self.app.db.fetch_all("SELECT id, first_name, last_name FROM patients WHERE is_active=1")
        for p in patients: self.cb_patient.addItem(f"{p['first_name']} {p['last_name']}", p['id'])
        form.addRow("Patient:", self.cb_patient)
        
        self.txt_amount = QtWidgets.QLineEdit()
        self.txt_amount.setPlaceholderText("ex: 50.0")
        form.addRow("Montant Total (DT):", self.txt_amount)
        
        self.txt_paid = QtWidgets.QLineEdit()
        self.txt_paid.setPlaceholderText("ex: 20.0 (Accompte)")
        form.addRow("Déjà payé / Accompte:", self.txt_paid)
        
        self.cb_status = QtWidgets.QComboBox()
        self.cb_status.addItems(["En attente", "Payé", "Partiel"])
        form.addRow("Statut:", self.cb_status)
        
        if self.inv_data:
            idx = self.cb_patient.findData(self.inv_data['patient_id'])
            if idx >= 0: self.cb_patient.setCurrentIndex(idx)
            self.txt_amount.setText(str(self.inv_data['total_amount']))
            self.txt_paid.setText(str(self.inv_data.get('paid_amount', 0)))
            self.cb_status.setCurrentText(self.inv_data['status'])

        l.addLayout(form)
        
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        l.addWidget(btns)

    def get_data(self):
        total = float(self.txt_amount.text() or 0)
        paid = float(self.txt_paid.text() or 0)
        # Calcul auto du statut
        status = self.cb_status.currentText()
        if paid >= total and total > 0:
            status = "Payé"
        elif paid > 0:
            status = "Partiel"
        else:
            status = "En attente"

        return {
            "patient_id": self.cb_patient.currentData(),
            "total_amount": total,
            "paid_amount": paid,
            "status": status,
            "created_at": QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        }

