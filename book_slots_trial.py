from app import app, db
from models import Slot
from datetime import date, time

with app.app_context():
    slot = Slot(
        venue_id=1,
        date=date(2025, 6, 5),
        start_time=time(8, 0),
        end_time=time(9, 0),
        is_booked = False
    )
    db.session.add(slot)
    db.session.commit()
