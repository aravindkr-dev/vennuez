from app import app, db
from models import TimeSlot

with app.app_context():
    slot_id = 6  # ID of the slot you want to update
    slot = TimeSlot.query.get(slot_id)

    if slot:
        slot.payment_status = 'paid'
        db.session.commit()
        print(f"Slot ID {slot_id} payment status updated to 'paid'.")
    else:
        print(f"No slot found with ID {slot_id}.")
