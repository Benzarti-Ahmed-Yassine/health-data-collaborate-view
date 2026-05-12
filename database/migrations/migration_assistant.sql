-- Migration Assistant: Tâches & Stock

CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT DEFAULT 'VACCIN',
    quantity INTEGER DEFAULT 0,
    min_threshold INTEGER DEFAULT 5,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    is_completed BOOLEAN DEFAULT 0,
    patient_id INTEGER,
    date_assigned DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(patient_id) REFERENCES patients(id)
);

-- Seed initial de l'inventaire
INSERT OR IGNORE INTO inventory (name, category, quantity, min_threshold) VALUES
('Vaccin Anti-Grippal', 'VACCIN', 15, 10),
('Sérum Tétanique', 'VACCIN', 8, 5),
('Seringues 5ml', 'MATERIEL', 100, 20),
('Gants Stériles', 'MATERIEL', 50, 15);
