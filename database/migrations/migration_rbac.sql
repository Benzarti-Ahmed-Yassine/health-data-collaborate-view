-- ============================================================
-- MIGRATION RBAC — Antigravity Role & Permission System
-- MediERP v2.0 (Ultra-Robust Version)
-- ============================================================

-- Foreign keys managed by DatabaseManager

-- 1. Réparation Table ROLES
CREATE TABLE IF NOT EXISTS roles_temp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    level INTEGER NOT NULL DEFAULT 1,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO roles_temp (id, name) SELECT id, name FROM roles;
DROP TABLE IF EXISTS roles;
ALTER TABLE roles_temp RENAME TO roles;

-- 2. Réparation Table PERMISSIONS
CREATE TABLE IF NOT EXISTS permissions_temp (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    resource TEXT,
    action TEXT,
    scope TEXT DEFAULT 'own',
    level INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Migrer anciennes si existent
INSERT OR IGNORE INTO permissions_temp (id, name)
SELECT CAST(id AS TEXT), name FROM permissions;

DROP TABLE IF EXISTS permissions;
ALTER TABLE permissions_temp RENAME TO permissions;

-- 3. Réparation Tables Jointures
CREATE TABLE IF NOT EXISTS role_permissions_v2 (
    role_id INTEGER NOT NULL,
    permission_id TEXT NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (permission_id) REFERENCES permissions(id)
);

CREATE TABLE IF NOT EXISTS user_roles (
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (role_id) REFERENCES roles(id)
);



-- 4. Seeds — Rôles
INSERT OR IGNORE INTO roles (id, name, level, description) VALUES
(1, 'PATIENT',   1, 'Patient - accès dossier personnel uniquement'),
(2, 'ASSISTANT', 2, 'Assistant médical - suivi patients, constantes vitales'),
(3, 'SECRETARY', 3, 'Secrétaire - agenda, contact patients, facturation basique'),
(4, 'DOCTOR',    4, 'Médecin - gestion patients, consultations, prescriptions'),
(5, 'ADMIN',     5, 'Administrateur - accès total au système');

-- 5. Seeds — Permissions
INSERT OR IGNORE INTO permissions (id, name, resource, action, scope, level) VALUES
-- Admin
('admin:view_dashboard',    'Voir dashboard admin',       'admin',       'view',   'all', 5),
('admin:manage_users',      'Gérer utilisateurs',         'users',       'manage', 'all', 5),
('admin:view_audit_logs',   'Voir les logs d''audit',     'audit',       'view',   'all', 5),
-- Doctor
('doctor:view_own_patients',     'Voir mes patients',          'patients',      'view',   'own',  4),
('doctor:manage_consultations',  'Gérer les consultations',    'consultations', 'manage', 'own',  4),
('doctor:create_prescriptions',  'Créer des ordonnances',      'prescriptions', 'create', 'own',  4),
-- Secretary
('secretary:manage_appointments',   'Gérer tous les RDV',       'appointments', 'manage', 'all', 3),
('secretary:view_billing',          'Voir facturation',         'invoices',     'view',   'all', 3),
-- Assistant
('assistant:record_vital_signs',     'Enregistrer constantes',    'vital_signs', 'create', 'own', 2),
-- Patient
('patient:view_own_profile',         'Voir mon profil',           'patients',      'view',   'self', 1);

-- (Ajouter d'autres permissions au besoin...)

-- 6. Mapping Rôles -> Permissions (Exemple simplifié pour le test)
INSERT OR IGNORE INTO role_permissions_v2 (role_id, permission_id)
SELECT 5, id FROM permissions; -- Admin a tout

INSERT OR IGNORE INTO role_permissions_v2 (role_id, permission_id)
SELECT 4, id FROM permissions WHERE id LIKE 'doctor:%';

INSERT OR IGNORE INTO role_permissions_v2 (role_id, permission_id)
SELECT 3, id FROM permissions WHERE id LIKE 'secretary:%';

INSERT OR IGNORE INTO role_permissions_v2 (role_id, permission_id)
SELECT 2, id FROM permissions WHERE id LIKE 'assistant:%';

INSERT OR IGNORE INTO role_permissions_v2 (role_id, permission_id)
SELECT 1, id FROM permissions WHERE id LIKE 'patient:%';

-- 7. Seeds — Utilisateurs & Rôles
-- Secrétaire
INSERT OR IGNORE INTO users (email, password_hash, full_name, role, is_active) VALUES
('secretary@medierp.ai', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G', 'Yassine Secrétaire', 'SECRETARY', 1);

INSERT OR IGNORE INTO user_roles (user_id, role_id)
SELECT id, 3 FROM users WHERE email = 'secretary@medierp.ai';

-- Patient
INSERT OR IGNORE INTO patients (cin, first_name, last_name, is_active) VALUES
('A100', 'Yassine', 'Benzarti', 1);

-- 8. Index
CREATE INDEX IF NOT EXISTS idx_user_roles_user ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_role_perms_role ON role_permissions_v2(role_id);
