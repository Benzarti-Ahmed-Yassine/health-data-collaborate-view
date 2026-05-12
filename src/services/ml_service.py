"""
Smart Medical AI - ML Service (Senior Edition)
Moteur de prédiction des risques cardiaques
Mode dégradé automatique si numpy/sklearn indisponibles
"""

import os
import math
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

# Import numpy de façon sécurisée — ne bloque jamais l'application
_numpy_available = False
try:
    import numpy as np
    _numpy_available = True
except Exception as e:
    logger.warning(f"[ML] numpy non disponible ({e}). Mode statistique activé.")

_sklearn_available = False
try:
    from sklearn.ensemble import RandomForestClassifier
    _sklearn_available = True
except Exception as e:
    logger.warning(f"[ML] sklearn non disponible ({e}). Mode statistique activé.")

_joblib_available = False
try:
    import joblib
    _joblib_available = True
except Exception as e:
    logger.warning(f"[ML] joblib non disponible ({e}). Mode statistique activé.")


class MLService:
    def __init__(self, model_path: str = "./assets/models/heart_risk_model.pkl"):
        self.model_path = model_path
        self.model = None
        self._mode = "STATISTICAL"   # 'ML' ou 'STATISTICAL'
        self._load_model()

    def _load_model(self):
        """Charge le modèle ML si disponible, sinon bascule en mode statistique."""
        if not (_numpy_available and _joblib_available):
            logger.warning("[ML] ⚠️ Bibliothèques ML absentes. Mode statistique (Framingham) activé.")
            self._mode = "STATISTICAL"
            return

        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                self._mode = "ML"
                logger.info(f"[ML] ✅ Modèle chargé: {self.model_path}")
            else:
                logger.warning("[ML] ⚠️ Fichier modèle manquant. Initialisation en mode statistique.")
                self._mode = "STATISTICAL"
                # Tenter de créer un modèle de base automatiquement
                self._auto_train()
        except Exception as e:
            logger.error(f"[ML] ❌ Erreur lors du chargement: {e}")
            self._mode = "STATISTICAL"

    def _auto_train(self):
        """Entraîne automatiquement un modèle de base si les libs sont disponibles."""
        if not (_numpy_available and _sklearn_available and _joblib_available):
            return
        try:
            logger.info("[ML] Entraînement automatique d'un modèle de base...")
            self.train_initial_model()
        except Exception as e:
            logger.warning(f"[ML] Entraînement automatique échoué: {e}")

    def train_initial_model(self, data_samples=None) -> bool:
        """Entraîne un modèle initial avec données synthétiques (Framingham-like)."""
        if not (_numpy_available and _sklearn_available and _joblib_available):
            logger.warning("[ML] Impossible d'entraîner: bibliothèques manquantes.")
            return False

        try:
            if data_samples is None:
                logger.info("[ML] Génération de données synthétiques...")
                import random
                random.seed(42)
                X, y = [], []
                for _ in range(1000):
                    age        = random.randint(20, 90)
                    bmi        = random.randint(18, 45)
                    systolic   = random.randint(90, 200)
                    cholest    = random.randint(150, 350)
                    smoker     = random.randint(0, 1)

                    risk_score = ((age - 30) * 0.1 + (systolic - 120) * 0.2
                                  + (cholest - 200) * 0.1 + smoker * 5
                                  + (bmi - 25) * 0.5)
                    # Sigmoïde manuelle sans numpy
                    risk_prob = 1 / (1 + math.exp(-0.1 * (risk_score - 10)))

                    X.append([age, bmi, systolic, cholest, smoker])
                    y.append(1 if random.random() < risk_prob else 0)

                X = np.array(X)
                y = np.array(y)
            else:
                X = np.array([s[:5] for s in data_samples])
                y = np.array([s[5] for s in data_samples])

            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X, y)
            self._mode = "ML"

            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)
            logger.info(f"[ML] ✅ Modèle sauvegardé: {self.model_path}")
            return True

        except Exception as e:
            logger.error(f"[ML] Erreur d'entraînement: {e}")
            return False

    def predict_risk(self, data: Dict[str, Any]) -> Tuple[int, str, str]:
        """
        Calcule le score de risque cardiaque (0–100).
        Utilise RandomForest si disponible, sinon algorithme Framingham.
        Retourne: (Score, Niveau, Explication)
        """
        if self.model is not None and _numpy_available:
            try:
                age        = float(data.get('age', 50))
                bmi        = float(data.get('bmi', 25))
                systolic   = float(data.get('systolic', 120))
                cholest    = float(data.get('cholesterol', 200))
                smoker     = 1 if data.get('smoker', False) else 0

                features = np.array([[age, bmi, systolic, cholest, smoker]])
                prob = self.model.predict_proba(features)[0][1]
                score = int(prob * 100)
                return score, *self._score_to_level(score)

            except Exception as e:
                logger.warning(f"[ML] Prédiction ML échouée ({e}), repli statistique.")

        return self._fallback_prediction(data)

    @staticmethod
    def _score_to_level(score: int):
        """Convertit un score numérique en (niveau, explication)."""
        if score < 15:
            return "LOW",    "Risque très faible. Excellents indicateurs."
        elif score < 40:
            return "LOW",    "Risque faible. Maintenir une surveillance annuelle."
        elif score < 70:
            return "MEDIUM", "Risque modéré. Hygiène de vie et suivi régulier recommandés."
        else:
            return "HIGH",   "Risque élevé. Intervention cardiologique et traitement préventif nécessaires."

    def _fallback_prediction(self, data: Dict[str, Any]) -> Tuple[int, str, str]:
        """Algorithme statistique Framingham-like (100% Python, sans numpy)."""
        age       = float(data.get('age', 50))
        systolic  = float(data.get('systolic', 120))
        cholest   = float(data.get('cholesterol', 200))
        smoker    = 1 if data.get('smoker', False) else 0
        bmi       = float(data.get('bmi', 25))

        score = 0.0
        score += (age - 30) * 0.4
        if systolic > 140: score += 12
        if systolic > 160: score += 8
        if cholest > 240:  score += 8
        if cholest > 300:  score += 6
        if smoker:         score += 15
        if bmi > 30:       score += 5
        if bmi > 35:       score += 5

        score = min(max(int(score), 5), 95)
        level, explanation = self._score_to_level(score)
        explanation += " (Analyse statistique — modèle ML non disponible)"
        return score, level, explanation

    @property
    def mode(self) -> str:
        """Retourne le mode actif: 'ML' ou 'STATISTICAL'."""
        return self._mode
