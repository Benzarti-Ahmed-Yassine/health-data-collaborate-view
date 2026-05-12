-- ============================================
-- MIGRATION 007: Messages & Notifications
-- Système de messagerie médecin-patient + notifications RDV
-- ============================================

-- Table messages (si pas encore créée)
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    sender_type TEXT NOT NULL DEFAULT 'USER',   -- 'USER' ou 'PATIENT'
    receiver_id INTEGER NOT NULL,
    receiver_type TEXT NOT NULL DEFAULT 'USER', -- 'USER' ou 'PATIENT'
    subject TEXT,
    body TEXT NOT NULL,
    is_read INTEGER DEFAULT 0,
    parent_message_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(parent_message_id) REFERENCES messages(id)
);

-- Table notifications in-app
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,           -- destinataire (user staff)
    patient_id INTEGER,        -- destinataire (patient)
    recipient_type TEXT DEFAULT 'USER',  -- 'USER' ou 'PATIENT'
    type TEXT NOT NULL,        -- 'MESSAGE', 'APPOINTMENT_CHANGE', 'APPOINTMENT_CONFIRMED', 'PRESCRIPTION'
    title TEXT NOT NULL,
    body TEXT,
    is_read INTEGER DEFAULT 0,
    reference_id INTEGER,      -- id du RDV, message, ou prescription
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ajouter colonne patient_id à vital_signs si absente
ALTER TABLE vital_signs ADD COLUMN patient_id INTEGER REFERENCES patients(id);

-- Ajouter colonne email à patients si absente (déjà dans schema mais par sécurité)
-- ALTER TABLE patients ADD COLUMN email TEXT;  -- commenté car déjà présent

-- Indexes pour performance
CREATE INDEX IF NOT EXISTS idx_messages_receiver ON messages(receiver_id, receiver_type);
CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id, sender_type);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_patient ON notifications(patient_id, is_read);
