-- ============================================
-- SMART MEDICAL AI - MIGRATION V3 (SECURITY)
-- ============================================

PRAGMA foreign_keys = ON;

-- 1. Table des Credentials
CREATE TABLE IF NOT EXISTS credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT CHECK(type IN ('password', 'api_token', 'biometric', '2fa', 'api_key')),
    value_hash TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    ip_addresses TEXT,  -- JSON array
    failed_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    created_by INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 2. Historique des Credentials
CREATE TABLE IF NOT EXISTS credential_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    credential_id INTEGER NOT NULL,
    action TEXT,  -- 'created', 'changed', 'rotated', 'revoked'
    old_value_hash TEXT,
    new_value_hash TEXT,
    changed_by INTEGER,
    reason TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT,
    FOREIGN KEY (credential_id) REFERENCES credentials(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(id)
);

-- 3. Audit des Credentials
CREATE TABLE IF NOT EXISTS credential_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT,  -- 'login', 'failed_login', 'token_issued', 'token_revoked'
    credential_type TEXT,
    status TEXT,  -- 'success', 'failed', 'locked'
    ip_address TEXT,
    user_agent TEXT,
    reason TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. Migration des données existantes
INSERT INTO credentials (user_id, type, value_hash, is_active)
SELECT id, 'password', password_hash, 1 FROM users
WHERE id NOT IN (SELECT user_id FROM credentials WHERE type = 'password');

-- 5. Indexation
CREATE INDEX IF NOT EXISTS idx_credentials_user ON credentials(user_id);
CREATE INDEX IF NOT EXISTS idx_credential_audit_user ON credential_audit(user_id);
