-- Fix messages table schema
-- 1. Rename old table
ALTER TABLE messages RENAME TO messages_old;

-- 2. Create new table with correct schema
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    sender_type TEXT DEFAULT 'USER',
    receiver_id INTEGER NOT NULL,
    receiver_type TEXT DEFAULT 'USER',
    subject TEXT,
    body TEXT NOT NULL,
    is_read INTEGER DEFAULT 0,
    parent_message_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(parent_message_id) REFERENCES messages(id)
);

-- 3. Migrate data (mapping 'message' to 'body')
INSERT INTO messages (id, sender_id, sender_type, receiver_id, body, is_read, created_at)
SELECT id, sender_id, sender_type, receiver_id, message, is_read, created_at 
FROM messages_old;

-- 4. Drop old table
DROP TABLE messages_old;

-- 5. Recreate indexes
CREATE INDEX idx_messages_receiver ON messages(receiver_id, receiver_type, is_read);
CREATE INDEX idx_messages_sender ON messages(sender_id, sender_type);
