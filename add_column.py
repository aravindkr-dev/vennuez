from app import db, app
from models import TimeSlot
from sqlalchemy import text

def add_number_of_people_column():
    try:
        # Add number_of_people column with default value 1
        db.session.execute(text('ALTER TABLE time_slots ADD COLUMN number_of_people INTEGER DEFAULT 1'))
        db.session.commit()
        print("Successfully added number_of_people column to time_slots table")
    except Exception as e:
        db.session.rollback()
        print(f"Error adding column: {str(e)}")

if __name__ == "__main__":
    with app.app_context():
        add_number_of_people_column() 