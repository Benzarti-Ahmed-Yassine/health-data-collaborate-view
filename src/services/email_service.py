import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.port = int(os.getenv("SMTP_PORT", 587))
        self.user = os.getenv("SMTP_USER")
        self.password = os.getenv("SMTP_PASSWORD")
        self.app_name = os.getenv("APP_NAME", "MediERP")

    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Envoie un email via SMTP."""
        if not self.user or not self.password:
            logger.warning("[Email] SMTP not configured in .env")
            return False

        server = None
        try:
            msg = MIMEMultipart()
            msg['From'] = f"{self.app_name} <{self.user}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            # FIX: Add timeout to prevent indefinite hangs
            server = smtplib.SMTP(self.host, self.port, timeout=10)
            server.starttls()
            server.login(self.user, self.password)
            server.send_message(msg)
            
            logger.info(f"[Email] Email sent to {to_email}: {subject}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"[Email] SMTP Authentication failed: {str(e)}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"[Email] SMTP error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"[Email] Unexpected error: {str(e)}")
            return False
        finally:
            if server:
                try:
                    server.quit()
                except:
                    pass

    def send_appointment_reminder(self, patient_email: str, patient_name: str, time: str):
        subject = f"Rappel de Rendez-vous - {self.app_name}"
        body = f"Bonjour {patient_name},\n\nCeci est un rappel pour votre rendez-vous prévu dans 30 minutes à {time}.\n\nCordialement,\nL'équipe {self.app_name}"
        return self.send_email(patient_email, subject, body)

    def notify_doctor_new_message(self, doctor_email: str, doctor_name: str, patient_name: str, subject: str) -> bool:
        email_subject = f"📩 Nouveau message patient - {self.app_name}"
        body = (
            f"Bonjour Dr. {doctor_name},\n\n"
            f"Vous avez reçu un nouveau message de votre patient(e) {patient_name}.\n\n"
            f"Objet : {subject}\n\n"
            f"Cordialement,\nL'équipe {self.app_name}"
        )
        return self.send_email(doctor_email, email_subject, body)

    def notify_patient_new_message(self, patient_email: str, patient_name: str, doctor_name: str) -> bool:
        subject = f"📩 Nouveau message de votre médecin - {self.app_name}"
        body = (
            f"Bonjour {patient_name},\n\n"
            f"Dr. {doctor_name} vient de vous envoyer un nouveau message sur MediERP.\n\n"
            f"Cordialement,\nL'équipe {self.app_name}"
        )
        return self.send_email(patient_email, subject, body)

    def notify_appointment_confirmed(self, recipient_email: str, recipient_name: str, date: str, by_name: str) -> bool:
        subject = f"✅ Rendez-vous confirmé - {self.app_name}"
        body = (
            f"Bonjour {recipient_name},\n\n"
            f"Votre rendez-vous du {date} a été confirmé par {by_name}.\n\n"
            f"Cordialement,\nL'équipe {self.app_name}"
        )
        return self.send_email(recipient_email, subject, body)

    def notify_secretary_change_request(self, secretary_email: str, patient_name: str, old_date: str, new_date: str, new_time: str) -> bool:
        subject = f"🔄 Demande de changement de rendez-vous - {self.app_name}"
        body = (
            f"Bonjour,\n\n"
            f"Le patient {patient_name} a demandé un changement pour son rendez-vous.\n\n"
            f"Ancienne date : {old_date}\n"
            f"Nouvelle date souhaitée : {new_date} à {new_time}\n\n"
            f"Merci de traiter cette demande dans le module de gestion des rendez-vous.\n\n"
            f"Cordialement,\nL'équipe {self.app_name}"
        )
        return self.send_email(secretary_email, subject, body)

    def notify_secretary_new_message(self, secretary_email: str, patient_name: str, subject: str, message_body: str) -> bool:
        email_subject = f"📩 Nouvelle demande patient (Secrétariat) - {self.app_name}"
        body = (
            f"Bonjour,\n\n"
            f"Vous avez reçu une nouvelle demande de {patient_name}.\n\n"
            f"Sujet : {subject}\n"
            f"Message :\n{message_body}\n\n"
            f"Merci de répondre via le portail MediERP.\n\n"
            f"Cordialement,\nL'équipe {self.app_name}"
        )
        return self.send_email(secretary_email, email_subject, body)

# Instance unique pour l'importation directe
email_service = EmailService()
