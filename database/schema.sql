-- ============================================
-- SMART MEDICAL AI - FULL DATABASE SCHEMA
-- SQLite3 / SQLCipher Ready
-- ============================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

-- ============================================
-- USERS & SECURITY (RBAC)
-- ============================================

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    phone TEXT,
    rpps_number TEXT,
    specialty TEXT,
    clinic_id INTEGER,
    role TEXT DEFAULT 'DOCTOR',
    is_active BOOLEAN DEFAULT 1,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS user_roles (
    user_id INTEGER,
    role_id INTEGER,
    PRIMARY KEY(user_id, role_id),
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(role_id) REFERENCES roles(id)
);

CREATE TABLE IF NOT EXISTS role_permissions (
    role_id INTEGER,
    permission_id INTEGER,
    PRIMARY KEY(role_id, permission_id),
    FOREIGN KEY(role_id) REFERENCES roles(id),
    FOREIGN KEY(permission_id) REFERENCES permissions(id)
);

-- ============================================
-- CLINIC (MULTI TENANT)
-- ============================================

CREATE TABLE IF NOT EXISTS clinics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    address TEXT,
    phone TEXT
);

-- ============================================
-- PATIENTS
-- ============================================

CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clinic_id INTEGER,
    cin TEXT UNIQUE,
    first_name TEXT,
    last_name TEXT,
    date_of_birth DATE,
    sex TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    city TEXT,
    blood_type TEXT,
    weight_kg REAL,
    height_cm REAL,
    is_active BOOLEAN DEFAULT 1,
    deleted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(clinic_id) REFERENCES clinics(id)
);

-- ============================================
-- MEDICAL RECORD
-- ============================================

CREATE TABLE IF NOT EXISTS medical_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    created_by INTEGER,
    status TEXT DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(patient_id) REFERENCES patients(id),
    FOREIGN KEY(created_by) REFERENCES users(id)
);

-- ============================================
-- CONSULTATIONS
-- ============================================

CREATE TABLE IF NOT EXISTS consultations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER,
    patient_id INTEGER,
    doctor_id INTEGER,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    diagnosis TEXT,
    notes TEXT,
    risk_score INTEGER,
    risk_level TEXT,
    status TEXT DEFAULT 'IN_PROGRESS',
    FOREIGN KEY(record_id) REFERENCES medical_records(id),
    FOREIGN KEY(patient_id) REFERENCES patients(id),
    FOREIGN KEY(doctor_id) REFERENCES users(id)
);

-- ============================================
-- VITAL SIGNS
-- ============================================

CREATE TABLE IF NOT EXISTS vital_signs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    consultation_id INTEGER,
    systolic_bp INTEGER,
    diastolic_bp INTEGER,
    heart_rate INTEGER,
    temperature REAL,
    spo2 REAL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(consultation_id) REFERENCES consultations(id)
);

-- ============================================
-- ALLERGIES
-- ============================================

CREATE TABLE IF NOT EXISTS allergies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    allergen TEXT,
    severity TEXT,
    FOREIGN KEY(patient_id) REFERENCES patients(id)
);

-- ============================================
-- MEDICATIONS
-- ============================================

CREATE TABLE IF NOT EXISTS medications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    default_dosage TEXT
);

-- ============================================
-- PRESCRIPTIONS
-- ============================================

CREATE TABLE IF NOT EXISTS prescriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    consultation_id INTEGER,
    patient_id INTEGER,
    doctor_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(consultation_id) REFERENCES consultations(id)
);

CREATE TABLE IF NOT EXISTS prescription_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prescription_id INTEGER,
    medication_id INTEGER,
    dosage TEXT,
    duration_days INTEGER,
    FOREIGN KEY(prescription_id) REFERENCES prescriptions(id)
);

-- ============================================
-- APPOINTMENTS
-- ============================================

CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    doctor_id INTEGER,
    scheduled_date DATE,
    scheduled_time TIME,
    status TEXT DEFAULT 'CONFIRMED', -- 'CONFIRMED', 'CANCELLED', 'CHANGE_REQUESTED', 'COMPLETED'
    pending_date DATE,
    pending_time TIME,
    FOREIGN KEY(patient_id) REFERENCES patients(id),
    FOREIGN KEY(doctor_id) REFERENCES users(id)
);

-- ============================================
-- BILLING
-- ============================================

CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    total_amount REAL,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(patient_id) REFERENCES patients(id)
);

CREATE TABLE IF NOT EXISTS invoice_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER,
    description TEXT,
    total_price REAL,
    FOREIGN KEY(invoice_id) REFERENCES invoices(id)
);

CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER,
    amount REAL,
    method TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(invoice_id) REFERENCES invoices(id)
);

-- ============================================
-- DOCUMENTS
-- ============================================

CREATE TABLE IF NOT EXISTS medical_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    consultation_id INTEGER,
    file_path TEXT,
    file_type TEXT,
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(patient_id) REFERENCES patients(id)
);

-- MESSAGES & NOTIFICATIONS REMOVED


-- ============================================
-- AI / ML
-- ============================================

CREATE TABLE IF NOT EXISTS ml_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    consultation_id INTEGER,
    risk_score INTEGER,
    risk_level TEXT,
    confidence REAL,
    model_version TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- AUDIT LOG (BLOCKCHAIN STYLE)
-- ============================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT,
    table_name TEXT,
    record_id INTEGER,
    old_value TEXT,
    new_value TEXT,
    previous_hash TEXT,
    current_hash TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX IF NOT EXISTS idx_patient_name ON patients(last_name, first_name);
CREATE INDEX IF NOT EXISTS idx_consultation_patient ON consultations(patient_id);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(scheduled_date);

-- ============================================
-- VIEWS
-- ============================================

CREATE VIEW IF NOT EXISTS v_patient_last_risk AS
SELECT 
    p.id,
    p.first_name,
    p.last_name,
    (SELECT risk_score FROM consultations c WHERE c.patient_id = p.id ORDER BY start_time DESC LIMIT 1) as risk_score
FROM patients p;

-- ============================================
-- SEED DATA
-- ============================================

INSERT OR IGNORE INTO roles (name) VALUES ('ADMIN'), ('DOCTOR'), ('SECRETARY'), ('ASSISTANT');

INSERT OR IGNORE INTO users (email, password_hash, full_name, role) VALUES
('yassine.admin@medierp.ai', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G', 'Yassine', 'ADMIN'),
('yassine.doctor@medierp.ai', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G', 'Dr. Yassine', 'DOCTOR'),
('yassine.secretary@medierp.ai', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G', 'Yassine', 'SECRETARY'),
('yassine.assistant@medierp.ai', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G', 'Yassine', 'ASSISTANT');
