"""
MediERP Professional - Biometric Widget
Interface de capture et d'authentification biométrique en temps réel.
"""

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
from ..utils.qt_compat import QtWidgets, QtCore, QtGui
from ..services.biometric_service import biometric_service
import time

class BiometricWidget(QtWidgets.QWidget):
    """
    Widget affichant le flux vidéo de la webcam avec détection de visage.
    """
    auth_success = QtCore.Signal(int)    # Émis lors d'une authentification réussie
    enrollment_complete = QtCore.Signal(bool)  # Émis après capture des samples

    def __init__(self, parent=None):
        super().__init__(parent)
        self.camera = None
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._update_frame)

        self.is_enrolling = False
        self.is_authenticating = False   # NEW: continuous auth mode flag
        self.enroll_user_id = None
        self.enroll_samples = 0
        self.max_samples = 5
        self._last_auth_attempt = 0      # NEW: cooldown tracker

        self._setup_ui()

    def __del__(self):
        """FIX: Ensure camera is released on cleanup"""
        self.stop_camera()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Label pour l'affichage vidéo
        self.video_label = QtWidgets.QLabel("Initialisation caméra...")
        self.video_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.video_label.setObjectName("video_label")
        self.video_label.setMinimumSize(400, 300)
        layout.addWidget(self.video_label)

        # Overlay de status
        self.status_label = QtWidgets.QLabel("En attente...")
        self.status_label.setObjectName("status_label")
        self.status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

    def start_camera(self):
        """Active la webcam."""
        if not CV2_AVAILABLE:
            self.status_label.setText("❌ Erreur: OpenCV non installé")
            return False
            
        if self.camera is None:
            try:
                self.camera = cv2.VideoCapture(0)
                if not self.camera.isOpened():
                    self.status_label.setText("❌ Erreur: Caméra non détectée")
                    self.camera.release()  # FIX: Release if failed to open
                    self.camera = None
                    return False
                self.timer.start(30)  # ~33 FPS
                self.status_label.setText("🎥 Caméra active")
                return True
            except Exception as e:
                import logging
                logging.error(f"Error starting camera: {str(e)}")
                if self.camera:
                    self.camera.release()
                    self.camera = None
                self.status_label.setText(f"❌ Erreur: {str(e)}")
                return False
        return False

    def stop_camera(self):
        """Désactive la webcam."""
        self.timer.stop()
        if self.camera:
            self.camera.release()
            self.camera = None
        self.video_label.setText("Caméra désactivée")

    def start_enrollment(self, user_id: int):
        """Lance le processus de capture pour enrôlement."""
        self.is_enrolling = True
        self.is_authenticating = False
        self.enroll_user_id = user_id
        self.enroll_samples = 0
        self.status_label.setText("🧬 Enrôlement: Regardez l'objectif...")

    def start_authentication(self):
        """Active le mode d'authentification continue (auto-détection)."""
        self.is_enrolling = False
        self.is_authenticating = True
        self._last_auth_attempt = 0
        self.status_label.setText("🔍 Positionnez votre visage face à la caméra...")

    def _update_frame(self):
        """Boucle principale de traitement d'image (Optimisée)."""
        if not self.camera:
            return
        ret, frame = self.camera.read()
        if not ret:
            return

        # Optimisation : Redimensionnement pour la détection (beaucoup plus rapide)
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        
        # Détection de visage pour le feedback visuel
        face_locations = biometric_service.get_face_locations(small_frame)

        display_frame = frame.copy()
        for (top, right, bottom, left) in face_locations:
            # Remettre à l'échelle originale (x4)
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            cv2.rectangle(display_frame, (left, top), (right, bottom), (24, 144, 255), 2)

        # — Mode Enrôlement —
        if self.is_enrolling and face_locations:
            if biometric_service.enroll_face(self.enroll_user_id, frame):
                self.enroll_samples += 1
                self.status_label.setText(f"🧬 Progression: {self.enroll_samples}/{self.max_samples}")

                if self.enroll_samples >= self.max_samples:
                    self.is_enrolling = False
                    self.status_label.setText("✅ Enrôlement terminé avec succès")
                    self.enrollment_complete.emit(True)

        # — Mode Authentification Continue —
        elif self.is_authenticating and face_locations:
            now = time.time()
            if now - self._last_auth_attempt >= 1.0:  # 1-second cooldown
                self._last_auth_attempt = now
                # On utilise la frame originale pour l'auth pour garder la précision
                success, user_id, confidence = biometric_service.authenticate(frame)
                if success and user_id:
                    self.is_authenticating = False
                    self.status_label.setText(f"✅ Identifié (confiance: {confidence:.0%})")
                    self.auth_success.emit(user_id)
                else:
                    self.status_label.setText(f"🔍 Reconnaissance en cours... ({len(face_locations)} visage(s))")

        # Conversion pour Qt
        rgb_image = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888)
        self.video_label.setPixmap(QtGui.QPixmap.fromImage(qt_image).scaled(
            self.video_label.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation
        ))

    def try_authenticate(self):
        """Tente d'authentifier le visage actuel (appel manuel)."""
        if not self.camera:
            return False

        ret, frame = self.camera.read()
        if ret:
            success, user_id, confidence = biometric_service.authenticate(frame)
            if success and user_id:
                self.status_label.setText(f"✅ Reconnu (ID: {user_id}, {confidence:.0%})")
                self.auth_success.emit(user_id)
                return True
        self.status_label.setText("❌ Identité non reconnue")
        return False
