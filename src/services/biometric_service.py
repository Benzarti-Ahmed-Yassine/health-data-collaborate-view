"""
MediERP Professional - Advanced Biometric Service
Reconnaissance faciale haute précision utilisant OpenCV et face_recognition.
"""

import os
import cv2
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BiometricService")

try:
    import face_recognition
    FACE_REC_AVAILABLE = True
except ImportError:
    FACE_REC_AVAILABLE = False
    logger.warning("face_recognition not installed. Biometric auth will be disabled.")

import numpy as np
import pickle
from typing import Optional, List, Tuple, Dict
from datetime import datetime

class BiometricService:
    """
    Service gérant l'enrôlement et l'authentification biométrique faciale.
    Utilise face_recognition (HOG/CNN) pour une précision supérieure.
    """

    def __init__(self, data_dir: str = "assets/biometrics/encodings"):
        self.data_dir = data_dir
        self._encodings: Dict[int, List[np.ndarray]] = {}
        
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"Création du répertoire biométrique: {self.data_dir}")
            
        self.load_encodings()

    def load_encodings(self):
        """Charge tous les encodages visages enregistrés."""
        try:
            encoding_files = [f for f in os.listdir(self.data_dir) if f.endswith('.pkl')]
            for file in encoding_files:
                try:
                    # Expected format: user_ID.pkl
                    parts = file.split('_')
                    if len(parts) < 2: continue
                    user_id = int(parts[1].split('.')[0])
                    with open(os.path.join(self.data_dir, file), 'rb') as f:
                        self._encodings[user_id] = pickle.load(f)
                except (ValueError, IndexError, pickle.UnpicklingError) as e:
                    logger.warning(f"Ignoré: fichier malformé {file} - {e}")
            logger.info(f"Chargement de {len(self._encodings)} utilisateurs biométriques.")
        except Exception as e:
            logger.error(f"Erreur lors du chargement des encodages: {e}")

    def enroll_face(self, user_id: int, frame: np.ndarray) -> bool:
        """
        Extrait l'encodage d'un visage depuis une frame et l'ajoute à l'utilisateur.
        """
        if not FACE_REC_AVAILABLE:
            return False
            
        try:
            # Conversion BGR (OpenCV) vers RGB (face_recognition)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Détection des visages
            face_locations = face_recognition.face_locations(rgb_frame)
            if not face_locations:
                logger.warning(f"Aucun visage détecté pour l'utilisateur {user_id}")
                return False
                
            # Encodage
            encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            if not encodings:
                return False
                
            encoding = encodings[0]
            
            if user_id not in self._encodings:
                self._encodings[user_id] = []
                
            self._encodings[user_id].append(encoding)
            
            # Sauvegarde persistante
            self._save_user_encodings(user_id)
            logger.info(f"Échantillon enregistré pour l'utilisateur {user_id} ({len(self._encodings[user_id])} samples)")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enrôlement: {e}")
            return False

    def _save_user_encodings(self, user_id: int):
        """Sauvegarde les encodages d'un utilisateur sur le disque."""
        file_path = os.path.join(self.data_dir, f"user_{user_id}.pkl")
        with open(file_path, 'wb') as f:
            pickle.dump(self._encodings[user_id], f)

    def authenticate(self, frame: np.ndarray, tolerance: float = 0.5) -> Tuple[bool, Optional[int], float]:
        """
        Compare le visage dans la frame avec tous les encodages connus.
        """
        if not FACE_REC_AVAILABLE:
            return False, None, 1.0
            
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            
            if not face_locations:
                return False, None, 1.0
                
            unknown_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            if not unknown_encodings:
                return False, None, 1.0
                
            unknown_encoding = unknown_encodings[0]
            
            best_match_id = None
            min_distance = 1.0
            
            for user_id, known_encodings in self._encodings.items():
                # Compare avec tous les samples de l'utilisateur
                distances = face_recognition.face_distance(known_encodings, unknown_encoding)
                avg_distance = np.mean(distances)
                
                if avg_distance < min_distance and avg_distance < tolerance:
                    min_distance = avg_distance
                    best_match_id = user_id
                    
            if best_match_id:
                confidence = 1.0 - min_distance
                logger.info(f"Authentification réussie pour ID {best_match_id} (Confiance: {confidence:.2f})")
                return True, best_match_id, confidence
                
            return False, None, min_distance
            
        except Exception as e:
            logger.error(f"Erreur lors de l'authentification: {e}")
            return False, None, 1.0

    def get_face_locations(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Détecte les visages pour affichage UI."""
        if not FACE_REC_AVAILABLE:
            return []
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return face_recognition.face_locations(rgb_frame)

# Instance singleton
biometric_service = BiometricService()
