from ...utils.qt_compat import QtWidgets, QtCore, QtGui
from ...core.app import SmartMedicalApp

class AuditView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header_layout = QtWidgets.QHBoxLayout()
        header_title = QtWidgets.QLabel("🔍 Audit & Conformité")
        header_title.setObjectName("header_title")
        header_layout.addWidget(header_title)
        header_layout.addStretch()

        self.btn_verify = QtWidgets.QPushButton("🛡️ Vérifier l'intégrité de la chaîne")
        self.btn_verify.setObjectName("btnSuccess")
        self.btn_verify.clicked.connect(self._verify_chain)
        header_layout.addWidget(self.btn_verify)
        layout.addLayout(header_layout)

        # Audit Table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date/Heure", "Utilisateur", "Action", "Ressource", "Signature (Hash)"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setObjectName("audit_table")
        layout.addWidget(self.table)

        self._load_audit_logs()

    def _load_audit_logs(self):
        try:
            logs = self.app.db.fetch_all("""
                SELECT timestamp, user_id, action, table_name, current_hash 
                FROM audit_logs ORDER BY id DESC LIMIT 50
            """)
            self.table.setRowCount(len(logs))
            for i, log in enumerate(logs):
                self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(log['timestamp'][:19]))
                self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(f"User #{log['user_id']}"))
                self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(log['action']))
                self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(log['table_name'] or "Système"))
                
                hash_item = QtWidgets.QTableWidgetItem(log['current_hash'][:16] + "...")
                hash_item.setToolTip(log['current_hash'])
                hash_item.setForeground(QtGui.QColor("#1890ff"))
                self.table.setItem(i, 4, hash_item)

        except Exception as e:
            print(f"Error loading audit logs: {e}")

    def _verify_chain(self):
        try:
            is_valid = self.app.security.verify_audit_chain()
            if is_valid:
                QtWidgets.QMessageBox.information(self, "Audit OK", "✅ L'intégrité de la base de données est garantie. Aucun log n'a été altéré.")
            else:
                QtWidgets.QMessageBox.critical(self, "ALERTE SÉCURITÉ", "❌ Rupture de chaîne détectée ! La base de données a peut-être été modifiée manuellement.")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Erreur", f"Échec de la vérification : {e}")

