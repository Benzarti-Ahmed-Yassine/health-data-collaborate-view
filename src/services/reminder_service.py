import threading
import time
import logging
from datetime import datetime, timedelta
from ..core.database import DatabaseManager
from .email_service import email_service

logger = logging.getLogger(__name__)

class ReminderService:
    def __init__(self):
        self.db = DatabaseManager()
        self.is_running = False
        self._thread = None

    def start(self):
        if self.is_running: return
        self.is_running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("[Reminder] Reminder service started (Interval: 5 min)")

    def _run(self):
        while self.is_running:
            try:
                self.check_reminders()
            except Exception as e:
                print(f"[Reminder] Erreur : {e}")
            time.sleep(300) # Check toutes les 5 mins

    def check_reminders(self):
        """Vérifie les rendez-vous prévus dans ~30 minutes."""
        now = datetime.now()
        target_date_str = now.strftime("%Y-%m-%d")
        
        # On cherche les rdv confirmés non encore rappelés pour aujourd'hui
        query = """
            SELECT a.id, p.email, p.first_name, a.scheduled_time 
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            WHERE a.scheduled_date = ? 
              AND a.status = 'CONFIRMED' 
              AND a.reminder_sent = 0
              AND p.email IS NOT NULL
        """
        appts = self.db.fetch_all(query, (target_date_str,))
        
        for a in appts:
            try:
                # Calcul de la différence
                appt_time_str = a['scheduled_time']
                if len(appt_time_str) == 5: appt_time_str += ":00" # HH:MM -> HH:MM:SS
                
                appt_time = datetime.strptime(f"{target_date_str} {appt_time_str}", "%Y-%m-%d %H:%M:%S")
                diff_minutes = (appt_time - now).total_seconds() / 60
                
                # Fenêtre de 30 minutes (on envoie entre 20 et 40 min avant)
                if 20 <= diff_minutes <= 40:
                    success = email_service.send_appointment_reminder(a['email'], a['first_name'], a['scheduled_time'])
                    if success:
                        # FIX: Use atomic update with WHERE clause to prevent race condition
                        updated = self.db.execute(
                            "UPDATE appointments SET reminder_sent = 1 WHERE id = ? AND reminder_sent = 0",
                            (a['id'],)
                        )
                        if updated:
                            logger.info(f"[Reminder] Rappel envoyé pour RDV ID {a['id']}")
                        else:
                            logger.debug(f"[Reminder] RDV {a['id']} déjà traité par un autre thread")
            except Exception as e:
                print(f"[Reminder] Erreur traitement RDV {a['id']} : {e}")

# Instance globale
reminder_service = ReminderService()
