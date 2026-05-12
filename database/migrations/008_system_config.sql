-- ============================================================
-- MIGRATION 008 — SYSTEM CONFIGURATION
-- Table pour stocker les paramètres dynamiques du système
-- ============================================================

CREATE TABLE IF NOT EXISTS system_config (
    key TEXT PRIMARY KEY,
    value TEXT,
    category TEXT DEFAULT 'GENERAL',
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed initial settings
INSERT OR IGNORE INTO system_config (key, value, category, description) VALUES
('maintenance_mode', '0', 'SYSTEM', 'Active le mode maintenance pour tous les utilisateurs non-admin'),
('auto_backup', '1', 'BACKUP', 'Lancement automatique d''une sauvegarde quotidienne'),
('backup_interval_hours', '24', 'BACKUP', 'Intervalle entre les sauvegardes automatiques'),
('face_auth_required', '0', 'SECURITY', 'Force l''authentification faciale pour le staff'),
('mfa_enabled', '0', 'SECURITY', 'Active la double authentification'),
('blockchain_audit_forced', '1', 'SECURITY', 'Garantit l''immuabilité des logs'),
('clinic_name', 'MediERP Medical Center', 'CLINIC', 'Nom de l''établissement'),
('clinic_address', '123 Avenue de la Santé, Tunis', 'CLINIC', 'Adresse physique'),
('clinic_phone', '+216 71 000 000', 'CLINIC', 'Numéro de téléphone'),
('clinic_email', 'contact@medierp.tn', 'CLINIC', 'Email de contact officiel');
