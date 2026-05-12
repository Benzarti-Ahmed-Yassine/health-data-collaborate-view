"""
MediERP — Doctor Messages View
Messagerie interne : le médecin consulte les messages patients et répond.
Notification email automatique à l'envoi.
"""

import logging
import threading
from ...utils.qt_compat import QtWidgets, QtCore, QtGui
from ...core.app import SmartMedicalApp
from ...core.events import EventType

logger = logging.getLogger(__name__)


class DoctorMessagesView(QtWidgets.QWidget):
    # Signal pour rafraîchissement thread-safe
    new_message_signal = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = SmartMedicalApp.get_instance()
        self._selected_message_id = None
        self._setup_ui()
        self.refresh_data()

        # Abonnement aux nouveaux messages entrants
        self.app.events.subscribe(EventType.MESSAGE_SENT, self._on_new_message_event)
        self.new_message_signal.connect(self.refresh_data)

        # Timer auto-refresh toutes les 30 secondes
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.refresh_data)
        self._timer.start(30000)

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

        # Header avec badge non lus
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("✉️ Messagerie")
        title.setObjectName("messages_title")
        header.addWidget(title)

        self.badge_unread = QtWidgets.QLabel("")
        self.badge_unread.setObjectName("badge_unread")
        self.badge_unread.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.badge_unread.setStyleSheet(
            "background-color: #ff4d4f; color: white; border-radius: 10px; "
            "padding: 2px 8px; font-weight: bold; font-size: 10pt;"
        )
        self.badge_unread.hide()
        header.addWidget(self.badge_unread)
        header.addStretch()
        left_layout.addLayout(header)

        # Bouton Nouveau message
        self.btn_new = QtWidgets.QPushButton("✍️  Écrire à un patient")
        self.btn_new.setFixedHeight(42)
        self.btn_new.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btn_new.setObjectName("btnPrimary")
        self.btn_new.clicked.connect(self._on_new_message)
        left_layout.addWidget(self.btn_new)

        # Filtre
        self.cb_filter = QtWidgets.QComboBox()
        self.cb_filter.addItems(["Tous les messages", "Non lus", "Envoyés"])
        self.cb_filter.currentIndexChanged.connect(self.refresh_data)
        left_layout.addWidget(self.cb_filter)

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
        self.txt_reply.setFixedHeight(100)
        self.txt_reply.setPlaceholderText("Écrivez votre réponse ici...")
        self.txt_reply.setObjectName("txt_reply")
        right_layout.addWidget(self.txt_reply)

        btn_row = QtWidgets.QHBoxLayout()
        self.btn_reply = QtWidgets.QPushButton("📤  Envoyer la réponse")
        self.btn_reply.setFixedHeight(42)
        self.btn_reply.setEnabled(False)
        self.btn_reply.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btn_reply.setObjectName("btnPrimary")
        self.btn_reply.clicked.connect(self._on_send_reply)
        btn_row.addWidget(self.btn_reply)

        self.btn_delete = QtWidgets.QPushButton("🗑️  Supprimer")
        self.btn_delete.setFixedHeight(42)
        self.btn_delete.setEnabled(False)
        self.btn_delete.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btn_delete.setObjectName("btnDanger")
        self.btn_delete.clicked.connect(self._on_delete_message)
        btn_row.addWidget(self.btn_delete)

        right_layout.addLayout(btn_row)
        main.addWidget(self.right, 3)

    # ================================================================
    # DATA
    # ================================================================

    def refresh_data(self):
        """Charge les messages du médecin connecté depuis la DB."""
        try:
            doctor_id = self.app.current_user_id()
            self.list_messages.clear()
            filter_idx = self.cb_filter.currentIndex()

            # Messages reçus (patients → médecin)
            if filter_idx == 2:  # Envoyés
                query = """
                    SELECT m.id, m.subject, m.body, m.is_read, m.created_at,
                           p.first_name || ' ' || p.last_name as sender_name,
                           'sent' as direction
                    FROM messages m
                    LEFT JOIN patients p ON m.receiver_id = p.id AND m.receiver_type = 'PATIENT'
                    WHERE m.sender_id = ? AND m.sender_type = 'USER'
                    ORDER BY m.created_at DESC
                """
                messages = self.app.db.fetch_all(query, (doctor_id,))
            else:
                unread_only = "AND m.is_read = 0" if filter_idx == 1 else ""
                query = f"""
                    SELECT m.id, m.subject, m.body, m.is_read, m.created_at,
                           p.first_name || ' ' || p.last_name as sender_name,
                           'received' as direction
                    FROM messages m
                    LEFT JOIN patients p ON m.sender_id = p.id AND m.sender_type = 'PATIENT'
                    WHERE m.receiver_id = ? AND m.receiver_type = 'USER'
                    {unread_only}
                    ORDER BY m.created_at DESC
                """
                messages = self.app.db.fetch_all(query, (doctor_id,))

            unread_count = 0
            for msg in messages:
                subject = msg['subject'] or "(Sans objet)"
                sender = msg['sender_name'] or "Patient"
                date_str = msg['created_at'][:10] if msg['created_at'] else ""
                is_unread = not msg['is_read'] and msg.get('direction') != 'sent'
                if is_unread:
                    unread_count += 1

                prefix = "📤 " if msg.get('direction') == 'sent' else ("🔵 " if is_unread else "")
                item = QtWidgets.QListWidgetItem(
                    f"{prefix}{subject}\n{sender} — {date_str}"
                )
                item.setData(QtCore.Qt.ItemDataRole.UserRole, msg['id'])

                if is_unread:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)

                self.list_messages.addItem(item)

            # Badge non lus
            if unread_count > 0:
                self.badge_unread.setText(str(unread_count))
                self.badge_unread.show()
            else:
                self.badge_unread.hide()

            if not messages:
                item = QtWidgets.QListWidgetItem("Aucun message.")
                item.setFlags(QtCore.Qt.ItemFlag.NoItemFlags)
                item.setForeground(QtGui.QBrush(QtGui.QColor("#bfbfbf")))
                self.list_messages.addItem(item)

        except Exception as e:
            print(f"[DoctorMessages] Erreur chargement: {e}")

    def _on_message_selected(self, current, previous):
        if not current:
            return
        msg_id = current.data(QtCore.Qt.ItemDataRole.UserRole)
        if not msg_id:
            return

        self._selected_message_id = msg_id
        self.btn_reply.setEnabled(True)
        self.btn_delete.setEnabled(True)

        try:
            query = """
                SELECT m.*,
                       p.first_name || ' ' || p.last_name as patient_name,
                       u.full_name as user_name
                FROM messages m
                LEFT JOIN patients p ON m.sender_id = p.id AND m.sender_type = 'PATIENT'
                LEFT JOIN users u ON m.sender_id = u.id AND m.sender_type = 'USER'
                WHERE m.id = ?
            """
            msg = self.app.db.fetch_one(query, (msg_id,))
            if not msg:
                return

            sender = msg['patient_name'] or msg['user_name'] or "Inconnu"
            self.lbl_subject.setText(msg['subject'] or "(Sans objet)")
            date_str = msg['created_at'][:16].replace('T', ' ') if msg['created_at'] else ""
            self.lbl_meta.setText(f"De : {sender}  •  {date_str}")
            self.txt_body.setPlainText(msg['body'] or "")

            # Marquer comme lu
            if not msg['is_read']:
                self.app.db.execute("UPDATE messages SET is_read = 1 WHERE id = ?", (msg_id,))
                font = current.font()
                font.setBold(False)
                current.setFont(font)
                txt = current.text().replace("🔵 ", "")
                current.setText(txt)
                self.refresh_data()

        except Exception as e:
            print(f"[DoctorMessages] Erreur affichage message {msg_id}: {e}")

    def _on_send_reply(self):
        if not self._selected_message_id:
            return

        body = self.txt_reply.toPlainText().strip()
        if not body:
            QtWidgets.QMessageBox.warning(self, "Réponse vide", "Veuillez écrire un message avant d'envoyer.")
            return

        try:
            doctor_id = self.app.current_user_id()
            doctor = self.app.current_user

            # Récupérer le message parent
            parent = self.app.db.fetch_one(
                "SELECT sender_id, sender_type, receiver_id, receiver_type, subject FROM messages WHERE id = ?",
                (self._selected_message_id,)
            )
            if not parent:
                return

            # Déterminer qui est le patient dans la conversation pour répondre au bon destinataire
            if parent['sender_type'] == 'PATIENT':
                target_id = parent['sender_id']
            else:
                target_id = parent['receiver_id']

            self.app.db.insert("messages", {
                "sender_id": doctor_id,
                "sender_type": "USER",
                "receiver_id": target_id,
                "receiver_type": "PATIENT",
                "subject": f"Re: {parent['subject'] or ''}",
                "body": body,
                "parent_message_id": self._selected_message_id,
            })

            # Notification in-app (via la nouvelle colonne patient_id)
            try:
                self.app.db.insert("notifications", {
                    "patient_id": target_id,
                    "title": "Réponse du médecin",
                    "message": f"Le Dr. {doctor.get('full_name', '')} a répondu à votre message.",
                })
            except Exception as e:
                logger.warning(f"Erreur notification in-app : {e}")

            # Notification email patient (en arrière-plan)
            patient = self.app.db.get_by_id("patients", parent['sender_id'])
            if patient and patient.get('email'):
                threading.Thread(
                    target=self._send_reply_email,
                    args=(patient, doctor),
                    daemon=True
                ).start()

            self.txt_reply.clear()
            QtWidgets.QMessageBox.information(self, "Envoyé", "Réponse envoyée avec succès.")
            self.refresh_data()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erreur", f"Impossible d'envoyer : {e}")

    def _send_reply_email(self, patient, doctor):
        from ...services.email_service import email_service
        email_service.notify_appointment_confirmed(
            patient['email'],
            f"{patient['first_name']} {patient['last_name']}",
            "une réponse",
            f"Dr. {doctor.get('full_name', '')}"
        )

    def _on_delete_message(self):
        if not self._selected_message_id:
            return
        reply = QtWidgets.QMessageBox.question(
            self, "Confirmation",
            "Supprimer ce message ?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.app.db.execute("DELETE FROM messages WHERE id = ?", (self._selected_message_id,))
            self._selected_message_id = None
            self.btn_reply.setEnabled(False)
            self.btn_delete.setEnabled(False)
            self.lbl_subject.setText("Sélectionnez un message")
            self.lbl_meta.setText("")
            self.txt_body.clear()
            self.refresh_data()

    def _on_new_message(self):
        """Compose un nouveau message vers un patient."""
        try:
            patients = self.app.db.fetch_all(
                "SELECT id, first_name, last_name FROM patients WHERE is_active = 1 ORDER BY last_name"
            )
            if not patients:
                QtWidgets.QMessageBox.information(self, "Info", "Aucun patient enregistré.")
                return

            dialog = _DoctorNewMessageDialog(patients, self)
            if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                doctor_id = self.app.current_user_id()

                msg_id = self.app.db.insert("messages", {
                    "sender_id": doctor_id,
                    "sender_type": "USER",
                    "receiver_id": data['patient_id'],
                    "receiver_type": "PATIENT",
                    "subject": data['subject'],
                    "body": data['body'],
                })

                # Notification in-app (via la nouvelle colonne patient_id)
                try:
                    self.app.db.insert("notifications", {
                        "patient_id": data['patient_id'],
                        "title": "Nouveau message de votre médecin",
                        "message": data['subject'],
                    })
                except Exception as e:
                    logger.warning(f"Erreur notification in-app : {e}")

                # Email en arrière-plan
                patient = self.app.db.get_by_id("patients", data['patient_id'])
                if patient and patient.get('email'):
                    doctor = self.app.current_user
                    threading.Thread(
                        target=self._notify_patient_email,
                        args=(patient, doctor, data['subject']),
                        daemon=True
                    ).start()

                self.app.events.emit(EventType.MESSAGE_SENT, {
                    "doctor_id": doctor_id,
                    "patient_id": data['patient_id']
                })
                QtWidgets.QMessageBox.information(self, "Envoyé", "Message envoyé au patient.")
                self.refresh_data()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erreur", f"Impossible d'envoyer : {e}")

    def _notify_patient_email(self, patient, doctor, subject):
        from ...services.email_service import email_service
        patient_name = f"{patient['first_name']} {patient['last_name']}"
        email_service.notify_doctor_new_message(
            patient['email'],
            patient_name,
            f"Dr. {doctor.get('full_name', '')}",
            subject
        )

    def _on_new_message_event(self, payload):
        """Appelé quand un patient envoie un message — rafraîchir la liste."""
        self.new_message_signal.emit()

    def search(self, text):
        """Filtre les messages par texte."""
        for i in range(self.list_messages.count()):
            item = self.list_messages.item(i)
            item.setHidden(text.lower() not in item.text().lower())


class _DoctorNewMessageDialog(QtWidgets.QDialog):
    """Dialog pour écrire un nouveau message à un patient."""

    def __init__(self, patients: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nouveau Message — Patient")
        self.setMinimumSize(580, 500)
        self.resize(580, 500)
        self._setup_ui(patients)

    def _setup_ui(self, patients):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QtWidgets.QLabel("✍️ Nouveau Message")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #0050b3;")
        layout.addWidget(title)

        form = QtWidgets.QFormLayout()
        form.setSpacing(14)

        self.cb_patient = QtWidgets.QComboBox()
        for p in patients:
            self.cb_patient.addItem(f"{p['first_name']} {p['last_name']}", p['id'])
        form.addRow("Destinataire :", self.cb_patient)

        self.txt_subject = QtWidgets.QLineEdit()
        self.txt_subject.setPlaceholderText("Ex: Résultats analyses, Rappel traitement…")
        self.txt_subject.setFixedHeight(40)
        form.addRow("Objet :", self.txt_subject)

        layout.addLayout(form)

        self.txt_body = QtWidgets.QTextEdit()
        self.txt_body.setPlaceholderText("Écrivez votre message ici...")
        self.txt_body.setMinimumHeight(200)
        layout.addWidget(self.txt_body)

        btns = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok |
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        btns.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setText("📤 Envoyer")
        btns.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setObjectName("btnPrimary")
        btns.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        btns.accepted.connect(self._on_accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _on_accept(self):
        if not self.txt_body.toPlainText().strip():
            QtWidgets.QMessageBox.warning(self, "Champ vide", "Le message ne peut pas être vide.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "patient_id": self.cb_patient.currentData(),
            "subject": self.txt_subject.text().strip() or "(Sans objet)",
            "body": self.txt_body.toPlainText().strip(),
        }
