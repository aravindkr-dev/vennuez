# Run this in your Flask shell (flask shell)
from app import app , db
from sqlalchemy import text
with app.app_context():
    with db.engine.connect() as conn:
        conn.execute(text("ALTER TABLE time_slots ADD COLUMN duration_hours REAL DEFAULT 1.0"))
        conn.commit()