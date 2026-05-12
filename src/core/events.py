"""
Smart Medical AI - Event Bus (Pattern Observer)
Communication asynchrone entre composants
"""

from typing import Callable, Dict, List, Any
from enum import Enum
import threading

class EventType(Enum):
    PATIENT_CREATED = "patient.created"
    PATIENT_UPDATED = "patient.updated"
    CONSULTATION_STARTED = "consultation.started"
    CONSULTATION_COMPLETED = "consultation.completed"
    ML_PREDICTION_READY = "ml.prediction_ready"
    ALERT_TRIGGERED = "alert.triggered"
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    INVOICE_CREATED = "invoice.created"
    INVOICE_UPDATED = "invoice.updated"
    APPOINTMENT_CREATED = "appointment.created"
    APPOINTMENT_UPDATED = "appointment.updated"
    APPOINTMENT_CONFIRMED = "appointment.confirmed"
    APPOINTMENT_CHANGE_REQUESTED = "appointment.change_requested"
    VITALS_RECORDED = "vitals.recorded"
    PATIENT_ARRIVED = "patient.arrived"
    MATERIAL_REQUESTED = "material.requested"
    MATERIAL_APPROVED = "material.approved"
    MESSAGE_SENT = "message.sent"
    PRESCRIPTION_CREATED = "prescription.created"



class EventBus:
    """
    Singleton Event Bus pour communication inter-composants.
    Thread-safe.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._subscribers: Dict[EventType, List[Callable]] = {}
                    cls._instance._history: List[dict] = []
        return cls._instance

    def subscribe(self, event_type: EventType, callback: Callable) -> None:
        """S'abonner à un événement"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: EventType, callback: Callable) -> None:
        """Se désabonner d'un événement"""
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                cb for cb in self._subscribers[event_type] if cb != callback
            ]

    def emit(self, event_type: EventType, payload: Any = None) -> None:
        """Émettre un événement à tous les abonnés"""
        event_data = {
            "type": event_type.value,
            "payload": payload,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        self._history.append(event_data)

        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(payload)
                except Exception as e:
                    print(f"[EventBus] Erreur callback {callback}: {e}")

    def get_history(self, event_type: EventType = None, limit: int = 100) -> List[dict]:
        """Récupérer l'historique des événements"""
        history = self._history
        if event_type:
            history = [h for h in history if h["type"] == event_type.value]
        return history[-limit:]

    def clear_history(self) -> None:
        """Vider l'historique"""
        self._history.clear()


# Instance globale
event_bus = EventBus()
