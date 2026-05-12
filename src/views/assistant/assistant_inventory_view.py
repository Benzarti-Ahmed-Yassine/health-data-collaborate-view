from ...utils.qt_compat import QtWidgets, QtCore, QtGui
from ...core.app import SmartMedicalApp

class AssistantInventoryView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self._setup_ui()
        self.refresh_data()

    def _setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Header
        header_layout = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("📦 Gestion des Stocks & Vaccins")
        title.setStyleSheet("font-size: 22pt; font-weight: bold; color: #1890ff;")
        
        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Rechercher un article...")
        self.search_bar.setFixedWidth(300)
        self.search_bar.setStyleSheet("padding: 8px; border: 1px solid #d9d9d9; border-radius: 6px; font-size: 11pt;")
        self.search_bar.textChanged.connect(self._filter_table)
        
        btn_req = QtWidgets.QPushButton("🔔 Demander Matériel")
        btn_req.setFixedSize(160, 40)
        btn_req.setStyleSheet("background-color: #faad14; color: white; border-radius: 8px; font-weight: bold;")
        btn_req.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        btn_req.clicked.connect(self._on_request_material)
        
        btn_add = QtWidgets.QPushButton("➕ Nouvel Article")
        btn_add.setFixedSize(160, 40)
        btn_add.setStyleSheet("background-color: #1890ff; color: white; border-radius: 8px; font-weight: bold;")
        btn_add.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self._add_item)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.search_bar)
        header_layout.addWidget(btn_req)
        header_layout.addWidget(btn_add)
        main_layout.addLayout(header_layout)

        # Table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Nom de l'article", "Catégorie", "Quantité", "Seuil d'alerte", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(5, 200)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setStyleSheet("""
            QTableWidget { border: 1px solid #e8e8e8; border-radius: 8px; background: white; }
            QHeaderView::section { background-color: #ffffff; padding: 10px; font-weight: bold; border: none; border-bottom: 1px solid #e8e8e8; }
            QTableWidget::item { padding: 10px; border-bottom: 1px solid #f0f0f0; }
        """)
        main_layout.addWidget(self.table)

    def refresh_data(self):
        self.table.setRowCount(0)
        items = self.app.db.fetch_all("SELECT id, name, category, quantity, min_threshold FROM inventory ORDER BY name")
        
        for row, item in enumerate(items):
            self.table.insertRow(row)
            
            # Formating
            item_id = str(item['id'])
            name = item['name']
            category = item['category']
            qty = int(item['quantity'])
            threshold = int(item['min_threshold'])
            
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(item_id))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(name))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(category))
            
            # Qty Cell with Alert Check
            qty_item = QtWidgets.QTableWidgetItem(str(qty))
            qty_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            if qty <= threshold:
                qty_item.setForeground(QtGui.QBrush(QtGui.QColor("#f5222d"))) # Red for low stock
                qty_item.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Weight.Bold))
                qty_item.setText(f"⚠️ {qty}")
            self.table.setItem(row, 3, qty_item)
            
            # Threshold Cell
            th_item = QtWidgets.QTableWidgetItem(str(threshold))
            th_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, th_item)
            
            # Actions Cell
            actions_widget = QtWidgets.QWidget()
            actions_layout = QtWidgets.QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)
            
            btn_edit_qty = QtWidgets.QPushButton("Mvt")
            btn_edit_qty.setStyleSheet("background-color: #52c41a; color: white; border-radius: 4px; padding: 5px;")
            btn_edit_qty.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            btn_edit_qty.clicked.connect(lambda checked, i=item_id, n=name, q=qty: self._update_quantity(i, n, q))
            
            btn_edit_th = QtWidgets.QPushButton("Seuil")
            btn_edit_th.setStyleSheet("background-color: #faad14; color: white; border-radius: 4px; padding: 5px;")
            btn_edit_th.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            btn_edit_th.clicked.connect(lambda checked, i=item_id, n=name, t=threshold: self._update_threshold(i, n, t))
            
            actions_layout.addWidget(btn_edit_qty)
            actions_layout.addWidget(btn_edit_th)
            self.table.setCellWidget(row, 5, actions_widget)

    def _add_item(self):
        name, ok1 = QtWidgets.QInputDialog.getText(self, "Nouvel Article", "Nom du vaccin/matériel :")
        if not ok1 or not name.strip(): return
        
        name = name.strip()
        existing = self.app.db.fetch_one("SELECT * FROM inventory WHERE LOWER(name) = LOWER(?)", (name,))
        if existing:
            QtWidgets.QMessageBox.warning(self, "Erreur", f"L'article '{name}' existe déjà dans l'inventaire.")
            return
            
        category, ok2 = QtWidgets.QInputDialog.getItem(self, "Catégorie", "Catégorie :", ["VACCIN", "MATERIEL", "AUTRE"], 0, False)
        if not ok2: return
        
        qty, ok3 = QtWidgets.QInputDialog.getInt(self, "Quantité", "Quantité initiale :", 0, 0, 10000)
        if not ok3: return
        
        threshold, ok4 = QtWidgets.QInputDialog.getInt(self, "Seuil", "Seuil d'alerte :", 5, 0, 10000)
        if not ok4: return
        
        self.app.db.execute("INSERT INTO inventory (name, category, quantity, min_threshold) VALUES (?, ?, ?, ?)", 
                            (name.strip(), category, qty, threshold))
        self.refresh_data()

    def _update_quantity(self, item_id, name, current_qty):
        qty, ok = QtWidgets.QInputDialog.getInt(self, f"Mouvement de Stock: {name}", "Nouvelle quantité totale :", current_qty, 0, 10000)
        if ok:
            self.app.db.execute("UPDATE inventory SET quantity = ? WHERE id = ?", (qty, item_id))
            self.refresh_data()

    def _update_threshold(self, item_id, name, current_threshold):
        th, ok = QtWidgets.QInputDialog.getInt(self, f"Modifier le Seuil: {name}", "Nouveau seuil d'alerte :", current_threshold, 0, 10000)
        if ok:
            self.app.db.execute("UPDATE inventory SET min_threshold = ? WHERE id = ?", (th, item_id))
            self.refresh_data()

    def _filter_table(self, text):
        search_term = text.lower()
        for row in range(self.table.rowCount()):
            item_name = self.table.item(row, 1).text().lower()
            category = self.table.item(row, 2).text().lower()
            match = search_term in item_name or search_term in category
            self.table.setRowHidden(row, not match)

    def search(self, text):
        """Méthode de recherche globale."""
        self.search_bar.setText(text)

    def _on_request_material(self):
        """Ouvre un dialogue pour demander du matériel au secrétaire."""
        name, ok1 = QtWidgets.QInputDialog.getText(self, "Demande de Matériel", "Article souhaité (Vaccin/Médicament/Autre) :")
        if not ok1 or not name.strip(): return
        
        qty, ok2 = QtWidgets.QInputDialog.getInt(self, "Quantité", "Quantité nécessaire :", 1, 1, 1000)
        if not ok2: return
        
        reason, ok3 = QtWidgets.QInputDialog.getText(self, "Raison", "Motif de la demande :")
        
        data = {
            "requester_id": self.app.current_user_id(),
            "item_name": name.strip(),
            "category": "MATERIAL",
            "quantity": qty,
            "reason": reason if ok3 else "",
            "status": "PENDING"
        }
        
        if self.app.db.insert("material_requests", data):
            QtWidgets.QMessageBox.information(self, "Demande Envoyée", "Votre demande a été transmise au secrétariat pour validation.")
            from ...core.events import EventType
            self.app.events.emit(EventType.MATERIAL_REQUESTED, data)
        else:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Impossible d'envoyer la demande.")
