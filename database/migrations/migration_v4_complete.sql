-- ============================================================
-- MIGRATION V4 COMPLETE — MediERP
-- Consolidation de toutes les tables/colonnes manquantes
-- Idempotente (IF NOT EXISTS / ADD COLUMN avec guard)
-- ============================================================

-- ============================================================
-- 1. APPOINTMENTS — Colonnes manquantes
-- ============================================================

-- Colonne 'arrived' : indique si le patient est arrivé en salle d'attente
ALTER TABLE appointments ADD COLUMN arrived INTEGER DEFAULT 0;
-- Guard: SQLite ne supporte pas "IF NOT EXISTS" sur ADD COLUMN
-- → SQLite ignore les erreurs de colonnes dupliquées si on utilise executescript,
--   mais on sécurise via le apply_migration qui ignore les OperationalError.

-- Colonne 'reminder_sent' : rappel email envoyé
ALTER TABLE appointments ADD COLUMN reminder_sent INTEGER DEFAULT 0;

-- Colonne 'scheduled_time' : heure du RDV (séparée de scheduled_date)
ALTER TABLE appointments ADD COLUMN scheduled_time TEXT;

-- Colonne 'notes' : notes optionnelles sur le RDV
ALTER TABLE appointments ADD COLUMN notes TEXT;

-- ============================================================
-- 2. USERS — Colonnes manquantes
-- ============================================================

-- Colonne 'photo_path' : chemin vers la photo de profil
ALTER TABLE users ADD COLUMN photo_path TEXT;

-- ============================================================
-- 3. MESSAGES — Table de messagerie interne
-- ============================================================

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,         -- user.id (staff) ou patient.id
    sender_type TEXT DEFAULT 'USER',    -- 'USER' ou 'PATIENT'
    receiver_id INTEGER NOT NULL,       -- user.id (staff) ou patient.id
    receiver_type TEXT DEFAULT 'USER',  -- 'USER' ou 'PATIENT'
    subject TEXT,
    body TEXT NOT NULL,
    is_read INTEGER DEFAULT 0,
    parent_message_id INTEGER,          -- Pour les réponses (thread)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(parent_message_id) REFERENCES messages(id)
);

-- ============================================================
-- 4. VITAL_SIGNS — Colonne patient_id directe (optimisation)
-- ============================================================

-- Actuellement vital_signs est lié à consultations, ce qui force
-- un JOIN systématique. On ajoute patient_id pour les requêtes rapides.
ALTER TABLE vital_signs ADD COLUMN patient_id INTEGER;

-- Backfill depuis consultations existantes
UPDATE vital_signs SET patient_id = (
    SELECT patient_id FROM consultations WHERE consultations.id = vital_signs.consultation_id
) WHERE patient_id IS NULL;

-- ============================================================
-- 5. PRESCRIPTIONS — Colonnes manquantes
-- ============================================================

-- S'assurer que doctor_id et notes existent
ALTER TABLE prescriptions ADD COLUMN doctor_id INTEGER;
ALTER TABLE prescriptions ADD COLUMN notes TEXT;
ALTER TABLE prescriptions ADD COLUMN status TEXT DEFAULT 'ACTIVE';

-- ============================================================
-- 6. MEDICAL_DOCUMENTS — Colonne uploaded_by
-- ============================================================

ALTER TABLE medical_documents ADD COLUMN uploaded_by INTEGER;
ALTER TABLE medical_documents ADD COLUMN description TEXT;

-- ============================================================
-- 7. INDEX SUPPLEMENTAIRES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_id);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);
CREATE INDEX IF NOT EXISTS idx_messages_receiver ON messages(receiver_id, receiver_type, is_read);
CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id, sender_type);
CREATE INDEX IF NOT EXISTS idx_vital_signs_patient ON vital_signs(patient_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_patient ON prescriptions(patient_id);

-- ============================================================
-- 8. SEED — Données de test supplémentaires
-- ============================================================

-- Patient test avec un compte user associé (pour login PATIENT via users)
INSERT OR IGNORE INTO users (email, password_hash, full_name, role, is_active)
VALUES ('patient@medierp.ai',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G',
        'Yassine Benzarti', 'PATIENT', 1);

-- Assistant test
INSERT OR IGNORE INTO users (email, password_hash, full_name, role, is_active)
VALUES ('assistant@medierp.ai',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G',
        'Yassine Assistant', 'ASSISTANT', 1);

-- Assigner rôles via user_roles pour les utilisateurs seeds
INSERT OR IGNORE INTO user_roles (user_id, role_id)
SELECT id, 2 FROM users WHERE email = 'assistant@medierp.ai';

INSERT OR IGNORE INTO user_roles (user_id, role_id)
SELECT id, 1 FROM users WHERE email = 'patient@medierp.ai';

-- Message de démonstration
INSERT OR IGNORE INTO messages (sender_id, sender_type, receiver_id, receiver_type, subject, body)
SELECT
    (SELECT id FROM users WHERE role='DOCTOR' LIMIT 1),
    'USER',
    (SELECT id FROM patients WHERE cin='A100' LIMIT 1),
    'PATIENT',
    'Résultats de votre consultation',
    'Bonjour,\n\nVos derniers résultats sont satisfaisants. Continuez votre traitement et revenez dans 3 mois.\n\nCordialement,\nDr. MediERP'
WHERE EXISTS (SELECT 1 FROM users WHERE role='DOCTOR')
  AND EXISTS (SELECT 1 FROM patients WHERE cin='A100');
