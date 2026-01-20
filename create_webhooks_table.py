"""Create webhooks table in SQLite database."""
import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Create webhooks table
cursor.execute("""
CREATE TABLE IF NOT EXISTS webhooks (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    url TEXT NOT NULL,
    event_type TEXT NOT NULL,
    is_active INTEGER DEFAULT 1 NOT NULL,
    max_retries INTEGER DEFAULT 5 NOT NULL,
    retry_count INTEGER DEFAULT 0 NOT NULL,
    status TEXT DEFAULT 'pending' NOT NULL,
    last_triggered_at TEXT,
    last_delivered_at TEXT,
    last_error TEXT,
    next_retry_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")

# Create indexes
cursor.execute("CREATE INDEX IF NOT EXISTS ix_webhooks_user_id ON webhooks(user_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS ix_webhooks_event_type ON webhooks(event_type)")
cursor.execute("CREATE INDEX IF NOT EXISTS ix_webhooks_status ON webhooks(status)")

conn.commit()
conn.close()

print("✅ Webhooks table created successfully!")
