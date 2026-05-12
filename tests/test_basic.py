"""
Smart Medical AI - Tests de base
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from core.database import DatabaseManager
from core.security import SecurityManager
from models.patient import Patient


class TestDatabase:
    """Tests base de données"""

    def test_connection(self):
        db = DatabaseManager()
        result = db.fetch_one("SELECT 1 as test")
        assert result["test"] == 1

    def test_patients_table_exists(self):
        db = DatabaseManager()
        result = db.fetch_one(
            """SELECT name FROM sqlite_master 
               WHERE type='table' AND name='patients'"""
        )
        assert result is not None

    def test_seed_data_loaded(self):
        db = DatabaseManager()
        result = db.fetch_one("SELECT COUNT(*) as count FROM patients")
        assert result["count"] >= 5


class TestSecurity:
    """Tests sécurité"""

    def test_password_hashing(self):
        sec = SecurityManager()
        password = "test123"
        hashed = sec.hash_password(password)
        assert sec.verify_password(password, hashed)
        assert not sec.verify_password("wrong", hashed)

    def test_authentication(self):
        sec = SecurityManager()
        result = sec.authenticate("didier@smartmedical.ai", "didier2026")
        assert result is not None
        assert result["role"] == "DOCTOR"


class TestPatient:
    """Tests modèle Patient"""

    def test_patient_search(self):
        patients = Patient.search("Jean")
        assert len(patients) > 0

    def test_patient_age(self):
        patient = Patient.get_by_id(1)
        if patient and patient.date_of_birth:
            assert patient.age is not None
            assert patient.age > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
