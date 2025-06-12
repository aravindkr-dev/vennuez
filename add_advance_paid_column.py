from app import db, app
from sqlalchemy import text

def add_advance_paid_column():
    try:
        db.session.execute(text('ALTER TABLE time_slots ADD COLUMN advance_paid REAL DEFAULT 0'))
        db.session.commit()
        print("Successfully added advance_paid column to time_slots table")
    except Exception as e:
        db.session.rollback()
        print(f"Error adding column: {str(e)}")

if __name__ == "__main__":
    with app.app_context():
        add_advance_paid_column() 