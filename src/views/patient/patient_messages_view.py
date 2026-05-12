"""
MediERP — Patient Messages View
Messagerie interne : le patient consulte et répond aux messages de son médecin.
"""

from ...utils.qt_compat import QtWidgets, QtCore, QtGui
from ...core.app import SmartMedicalApp


class PatientMessagesView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self._selected_message_id = None
        self._setup_ui()
        self.refresh_data()

    # ================================================================
    # UI SETUP
    # ================================================================

    def _setup_ui(self):
        main = QtWidgets.QHBoxLayout(self)
        main.setContentsMargins(30, 30, 30, 30)
        main.setSpacing(20)

        # ── Colonne gauche : Liste des messages
        left = QtWidgets.QFrame()
        left.setObjectName("messages_left")
        left_layout = QtWidgets.QVBoxLayout(left)
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.setSpacing(12)

        # Titre
        title = QtWidgets.QLabel("✉️ Mes Messages")
        title.setObjectName("messages_title")
        left_layout.addWidget(title)

        # Bouton Nouveau message
        self.btn_new = QtWidgets.QPushButton("✍️  Écrire au Médecin")
        self.btn_new.setFixedHeight(42)
        self.btn_new.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btn_new.setObjectName("btnWarning")
        self.btn_new.clicked.connect(self._on_new_message)
        left_layout.addWidget(self.btn_new)

        self.btn_request_rdv = QtWidgets.QPushButton("📅  Demander un RDV / Confirmation")
        self.btn_request_rdv.setFixedHeight(42)
        self.btn_request_rdv.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btn_request_rdv.setStyleSheet("background-color: #13c2c2; color: white; font-weight: bold; border-radius: 6px;")
        self.btn_request_rdv.clicked.connect(self._on_request_rdv)
        left_layout.addWidget(self.btn_request_rdv)

        # Liste des messages
        self.list_messages = QtWidgets.QListWidget()
        self.list_messages.setObjectName("list_messages")
        self.list_messages.currentItemChanged.connect(self._on_message_selected)
        left_layout.addWidget(self.list_messages)

        main.addWidget(left, 2)

        # ── Colonne droite : Détail du message
        self.right = QtWidgets.QFrame()
        self.right.setObjectName("messages_right")
        right_layout = QtWidgets.QVBoxLayout(self.right)
        right_layout.setContentsMargins(24, 24, 24, 24)
        right_layout.setSpacing(16)

        self.lbl_subject = QtWidgets.QLabel("Sélectionnez un message")
        self.lbl_subject.setObjectName("msg_subject")
        self.lbl_subject.setWordWrap(True)
        right_layout.addWidget(self.lbl_subject)

        self.lbl_meta = QtWidgets.QLabel("")
        self.lbl_meta.setObjectName("msg_meta")
        right_layout.addWidget(self.lbl_meta)

        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        separator.setObjectName("msg_separator")
        right_layout.addWidget(separator)

        self.txt_body = QtWidgets.QTextEdit()
        self.txt_body.setReadOnly(True)
        self.txt_body.setObjectName("msg_body")
        right_layout.addWidget(self.txt_body, 1)

        # Zone de réponse
        reply_lbl = QtWidgets.QLabel("Votre réponse :")
        reply_lbl.setObjectName("reply_label")
        right_layout.addWidget(reply_lbl)

        self.txt_reply = QtWidgets.QTextEdit()
        self.txt_reply.setFixedHeight(90)
        self.txt_reply.setPlaceholderText("Écrivez votre réponse ici...")
        self.txt_reply.setObjectName("txt_reply")
        right_layout.addWidget(self.txt_reply)

        self.btn_reply = QtWidgets.QPushButton("📤  Envoyer la réponse")
        self.btn_reply.setFixedHeight(42)
        self.btn_reply.setEnabled(False)
        self.btn_reply.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btn_reply.setObjectName("btnReply")
        self.btn_reply.clicked.connect(self._on_send_reply)
        right_layout.addWidget(self.btn_reply)

        main.addWidget(self.right, 3)

    # ================================================================
    # DATA
    # ================================================================

    def refresh_data(self):
        """Charge les messages du patient connecté."""
        try:
            pid = self.app.current_user_id()
            self.list_messages.clear()

            query = """
                SELECT m.id, m.subject, m.body, m.is_read, m.created_at,
                       u.full_name as sender_name
                FROM messages m
                LEFT JOIN users u ON m.sender_id = u.id AND m.sender_type = 'USER'
                WHERE m.receiver_id = ? AND m.receiver_type = 'PATIENT'
                ORDER BY m.created_at DESC
            """
            messages = self.app.db.fetch_all(query, (pid,))

            for msg in messages:
                subject = msg['subject'] or "(Sans objet)"
                sender = msg['sender_name'] or "Médecin"
                date_str = msg['created_at'][:10] if msg['created_at'] else ""
                unread_mark = "🔵 " if not msg['is_read'] else ""

                item = QtWidgets.QListWidgetItem(
                    f"{unread_mark}{subject}\n{sender} — {date_str}"
                )
                item.setData(QtCore.Qt.ItemDataRole.UserRole, msg['id'])

                if not msg['is_read']:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)

                self.list_messages.addItem(item)

            if not messages:
                item = QtWidgets.QListWidgetItem("Aucun message pour l'instant.")
                item.setFlags(QtCore.Qt.ItemFlag.NoItemFlags)
                item.setForeground(QtGui.QBrush(QtGui.QColor("#bfbfbf")))
                self.list_messages.addItem(item)

        except Exception as e:
            print(f"[PatientMessages] Erreur chargement: {e}")

    def _on_message_selected(self, current, previous):
        if not current:
            return
        msg_id = current.data(QtCore.Qt.ItemDataRole.UserRole)
        if not msg_id:
            return

        self._selected_message_id = msg_id
        self.btn_reply.setEnabled(True)

        try:
            query = """
                SELECT m.*, u.full_name as sender_name
                FROM messages m
                LEFT JOIN users u ON m.sender_id = u.id AND m.sender_type = 'USER'
                WHERE m.id = ?
            """
            msg = self.app.db.fetch_one(query, (msg_id,))
            if not msg:
                return

            self.lbl_subject.setText(msg['subject'] or "(Sans objet)")
            date_str = msg['created_at'][:16].replace('T', ' ') if msg['created_at'] else ""
            self.lbl_meta.setText(f"De : {msg['sender_name'] or 'Médecin'}  •  {date_str}")
            self.txt_body.setPlainText(msg['body'] or "")

            # Marquer comme lu
            if not msg['is_read']:
                self.app.db.execute(
                    "UPDATE messages SET is_read = 1 WHERE id = ?", (msg_id,)
                )
                # Retirer le bold de la liste
                font = current.font()
                font.setBold(False)
                current.setFont(font)
                txt = current.text().replace("🔵 ", "")
                current.setText(txt)

        except Exception as e:
            print(f"[PatientMessages] Erreur affichage message {msg_id}: {e}")

    def _on_send_reply(self):
        if not self._selected_message_id:
            return

        body = self.txt_reply.toPlainText().strip()
        if not body:
            QtWidgets.QMessageBox.warning(self, "Réponse vide", "Veuillez écrire un message avant d'envoyer.")
            return

        try:
            pid = self.app.current_user_id()
            # Récupérer le message parent pour connaître le destinataire
            parent = self.app.db.fetch_one(
                "SELECT sender_id, sender_type, subject FROM messages WHERE id = ?",
                (self._selected_message_id,)
            )
            if not parent:
                return

            self.app.db.insert("messages", {
                "sender_id": pid,
                "sender_type": "PATIENT",
                "receiver_id": parent['sender_id'],
                "receiver_type": parent['sender_type'],
                "subject": f"Re: {parent['subject'] or ''}",
                "body": body,
                "parent_message_id": self._selected_message_id,
            })

            self.txt_reply.clear()
            QtWidgets.QMessageBox.information(
                self, "Envoyé", "Votre message a été envoyé au médecin."
            )
            self.refresh_data()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erreur", f"Impossible d'envoyer : {e}")

    def _on_new_message(self):
        """Compose un nouveau message vers le médecin traitant."""
        try:
            pid = self.app.current_user_id()

            doctors = self.app.db.fetch_all(
                "SELECT id, full_name, email FROM users WHERE role = 'DOCTOR' AND is_active = 1"
            )
            if not doctors:
                QtWidgets.QMessageBox.information(
                    self, "Info", "Aucun médecin disponible pour recevoir un message."
                )
                return

            dialog = _NewMessageDialog(doctors, self)
            if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                data = dialog.get_data()

                msg_id = self.app.db.insert("messages", {
                    "sender_id": pid,
                    "sender_type": "PATIENT",
                    "receiver_id": data['doctor_id'],
                    "receiver_type": "USER",
                    "subject": data['subject'],
                    "body": data['body'],
                })

                # Notification in-app médecin
                self.app.db.insert("notifications", {
                    "user_id": data['doctor_id'],
                    "title": "Nouveau message patient",
                    "message": f"Sujet : {data['subject']}",
                })

                # Email médecin en arrière-plan
                doctor = next((d for d in doctors if d['id'] == data['doctor_id']), None)
                patient = self.app.db.get_by_id("patients", pid)
                if doctor and doctor.get('email') and patient:
                    import threading
                    def _email():
                        from ...services.email_service import email_service
                        email_service.notify_doctor_new_message(
                            doctor['email'],
                            doctor.get('full_name', ''),
                            f"{patient['first_name']} {patient['last_name']}",
                            data['subject']
                        )
                    threading.Thread(target=_email, daemon=True).start()

                from ...core.events import EventType
                self.app.events.emit(EventType.MESSAGE_SENT, {
                    "patient_id": pid, "doctor_id": data['doctor_id']
                })

                QtWidgets.QMessageBox.information(
                    self, "Envoyé", "Votre message a été envoyé au médecin."
                )
                self.refresh_data()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erreur", f"Impossible d'envoyer : {e}")

    def _on_request_rdv(self):
        """Permet au patient de demander un RDV ou une confirmation à la secrétaire."""
        try:
            pid = self.app.current_user_id()
            # Chercher une secrétaire active (on récupère aussi l'email)
            secretary = self.app.db.fetch_one(
                "SELECT id, full_name, email FROM users WHERE role = 'SECRETARY' AND is_active = 1 LIMIT 1"
            )
            if not secretary:
                QtWidgets.QMessageBox.warning(
                    self, "Indisponible", "Aucun service de secrétariat n'est disponible pour le moment."
                )
                return

            text, ok = QtWidgets.QInputDialog.getMultiLineText(
                self, "Demande Secrétariat",
                "Précisez votre demande (changement de RDV, confirmation, etc.) :",
                "Bonjour, je souhaiterais..."
            )
            
            if ok and text.strip():
                subject = "📅 Demande de RDV / Confirmation"
                msg_body = text.strip()
                
                msg_id = self.app.db.insert("messages", {
                    "sender_id": pid,
                    "sender_type": "PATIENT",
                    "receiver_id": secretary['id'],
                    "receiver_type": "USER",
                    "subject": subject,
                    "body": msg_body,
                })
                
                # Notification in-app secrétaire
                self.app.db.insert("notifications", {
                    "user_id": secretary['id'],
                    "title": "Nouvelle demande de RDV",
                    "message": f"Un patient a envoyé une demande de rendez-vous.",
                })
                
                # Email Secrétaire en arrière-plan
                patient = self.app.db.get_by_id("patients", pid)
                if secretary.get('email') and patient:
                    import threading
                    def _notify_sec():
                        try:
                            from ...services.email_service import email_service
                            email_service.notify_secretary_new_message(
                                secretary['email'],
                                f"{patient['first_name']} {patient['last_name']}",
                                subject,
                                msg_body
                            )
                        except Exception as e:
                            print(f"Error notifying secretary by email: {e}")
                    
                    threading.Thread(target=_notify_sec, daemon=True).start()
                
                QtWidgets.QMessageBox.information(
                    self, "Envoyé", "Votre demande a été transmise au secrétariat par messagerie et email."
                )
                self.refresh_data()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erreur", f"Échec de l'envoi : {e}")


class _NewMessageDialog(QtWidgets.QDialog):
    """Dialog de composition d'un nouveau message."""

    def __init__(self, doctors: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nouveau Message")
        self.setMinimumSize(600, 700)
        self.resize(600, 700)
        self._setup_ui(doctors)

    def _setup_ui(self, doctors):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QtWidgets.QFrame()
        header.setFixedHeight(70)
        header.setObjectName("newmsg_header")
        h_layout = QtWidgets.QHBoxLayout(header)
        lbl_title = QtWidgets.QLabel("✍️ Nouveau Message")
        lbl_title.setObjectName("newmsg_title")
        h_layout.addWidget(lbl_title)
        layout.addWidget(header)

        # Form content
        content = QtWidgets.QFrame()
        content.setObjectName("newmsg_content")
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)

        form = QtWidgets.QFormLayout()
        form.setSpacing(15)
        form.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        lbl_doc = QtWidgets.QLabel("Destinataire :")
        lbl_doc.setObjectName("form_label")
        self.cb_doctor = QtWidgets.QComboBox()
        for d in doctors:
            self.cb_doctor.addItem(d['full_name'], d['id'])
        self.cb_doctor.setObjectName("form_select")
        form.addRow(lbl_doc, self.cb_doctor)

        lbl_sub = QtWidgets.QLabel("Objet :")
        lbl_sub.setObjectName("form_label")
        self.txt_subject = QtWidgets.QLineEdit()
        self.txt_subject.setPlaceholderText("Ex: Question sur mon traitement")
        self.txt_subject.setObjectName("form_input")
        form.addRow(lbl_sub, self.txt_subject)

        content_layout.addLayout(form)

        self.txt_body = QtWidgets.QTextEdit()
        self.txt_body.setPlaceholderText("Écrivez votre message ici...")
        self.txt_body.setMinimumHeight(180)
        self.txt_body.setObjectName("form_textarea")
        content_layout.addWidget(self.txt_body)

        btns = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok |
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        btns.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setText("Envoyer")
        btns.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        btns.button(QtWidgets.QDialogButtonBox.StandardButton.Cancel).setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        
        # Apply primary style to OK button
        btns.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setObjectName("btnPrimary")
        
        btns.accepted.connect(self._on_accept)
        btns.rejected.connect(self.reject)
        content_layout.addWidget(btns)
        
        layout.addWidget(content)

    def _on_accept(self):
        if not self.txt_body.toPlainText().strip():
            QtWidgets.QMessageBox.warning(self, "Champ vide", "Le message ne peut pas être vide.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "doctor_id": self.cb_doctor.currentData(),
            "subject": self.txt_subject.text().strip() or "(Sans objet)",
            "body": self.txt_body.toPlainText().strip(),
        }
