from app import db , app
from sqlalchemy import text
with app.app_context():
    result = db.session.execute(text('PRAGMA table_info(time_slots);'))
    for row in result:
        print(row)