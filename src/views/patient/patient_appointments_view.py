from ...utils.qt_compat import QtWidgets, QtCore, QtGui
from ...core.app import SmartMedicalApp

class PatientAppointmentsView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header = QtWidgets.QLabel("📅 Mes Rendez-vous")
        header.setStyleSheet("font-size: 20pt; font-weight: bold; color: #fa8c16;")
        layout.addWidget(header)

        # Table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date/Heure", "Médecin", "Statut", "Modif. en attente", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #f0f0f0;")
        layout.addWidget(self.table)

        self._load_appointments()

    def _load_appointments(self):
        try:
            patient_id = self.app.current_user_id()
            query = """
                SELECT a.id, a.scheduled_date, u.full_name as doctor_name, a.status, a.pending_date, a.pending_time
                FROM appointments a
                JOIN users u ON a.doctor_id = u.id
                WHERE a.patient_id = ?
                ORDER BY a.scheduled_date DESC
            """
            rdvs = self.app.db.fetch_all(query, (patient_id,))
            self.table.setRowCount(len(rdvs))
            for i, r in enumerate(rdvs):
                self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(r['scheduled_date']))
                self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(r['doctor_name']))
                
                status_item = QtWidgets.QTableWidgetItem(r['status'])
                if r['status'] == 'CHANGE_REQUESTED':
                    status_item.setForeground(QtGui.QColor("#faad14"))
                    status_item.setText("Changement demandé")
                self.table.setItem(i, 2, status_item)

                pending = f"{r['pending_date']} {r['pending_time']}" if r['pending_date'] else "--"
                self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(pending))

                # Actions
                btn_req = QtWidgets.QPushButton("🔄 Modifier")
                btn_req.setEnabled(r['status'] == 'CONFIRMED')
                btn_req.clicked.connect(lambda checked, aid=r['id']: self._on_request_change(aid))
                self.table.setCellWidget(i, 4, btn_req)

        except Exception as e:
            print(f"Error loading patient appointments: {e}")

    def _on_request_change(self, aid):
        dt, ok = QtWidgets.QInputDialog.getText(self, "Demander Modification", "Nouvelle date/heure (AAAA-MM-JJ HH:MM) :")
        if ok and dt:
            try:
                parts = dt.split()
                if len(parts) != 2: raise ValueError("Format invalide : Utilisez 'AAAA-MM-JJ HH:MM'")
                
                # Récupérer les infos pour l'email AVANT la mise à jour
                query_info = """
                    SELECT a.scheduled_date, p.first_name || ' ' || p.last_name as patient_name
                    FROM appointments a
                    JOIN patients p ON a.patient_id = p.id
                    WHERE a.id = ?
                """
                info = self.app.db.fetch_one(query_info, (aid,))
                
                data = {
                    "status": "CHANGE_REQUESTED",
                    "pending_date": parts[0],
                    "pending_time": parts[1]
                }
                
                if self.app.db.update("appointments", aid, data):
                    QtWidgets.QMessageBox.information(self, "Succès", "Votre demande a été envoyée au secrétariat.")
                    
                    # Notification par Email au Secrétaire
                    try:
                        # On cherche le premier secrétaire actif
                        sec_user = self.app.db.fetch_one("SELECT email FROM users WHERE role = 'SECRETARY' AND is_active = 1 LIMIT 1")
                        
                        if sec_user and sec_user['email'] and info:
                            import threading
                            def _notify_email():
                                try:
                                    from ...services.email_service import email_service
                                    email_service.notify_secretary_change_request(
                                        secretary_email=sec_user['email'],
                                        patient_name=info['patient_name'],
                                        old_date=info['scheduled_date'],
                                        new_date=parts[0],
                                        new_time=parts[1]
                                    )
                                except Exception as inner_e:
                                    print(f"Erreur thread email: {inner_e}")
                                    
                            threading.Thread(target=_notify_email, daemon=True).start()
                    except Exception as e_mail:
                        print(f"Erreur notification email secrétaire: {e_mail}")

                    self._load_appointments()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Erreur", f"Erreur lors de la demande : {e}")

