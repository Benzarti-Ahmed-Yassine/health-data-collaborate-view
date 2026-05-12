-- Migration: Feature updates for search, material validation, and deposits
-- 1. Invoices updates for deposits (acomptes)
ALTER TABLE invoices ADD COLUMN paid_amount REAL DEFAULT 0;

-- 2. Material requests table for Assistant -> Secretary workflow
CREATE TABLE IF NOT EXISTS material_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requester_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    category TEXT, -- 'MATERIAL', 'VACCINE', 'MEDICINE'
    quantity INTEGER DEFAULT 1,
    estimated_cost REAL,
    reason TEXT,
    status TEXT DEFAULT 'PENDING', -- 'PENDING', 'APPROVED', 'REJECTED'
    validator_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    validated_at TIMESTAMP,
    FOREIGN KEY(requester_id) REFERENCES users(id),
    FOREIGN KEY(validator_id) REFERENCES users(id)
);
