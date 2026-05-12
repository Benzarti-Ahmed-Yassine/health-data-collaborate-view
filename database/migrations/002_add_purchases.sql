-- Migration: Add purchases table for material management
CREATE TABLE IF NOT EXISTS purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    category TEXT, -- 'MATERIAL', 'MEDICINE', 'OFFICE', 'OTHER'
    quantity INTEGER,
    unit_price REAL,
    total_price REAL,
    supplier TEXT,
    purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
