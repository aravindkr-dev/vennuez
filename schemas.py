from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models import *
from marshmallow import fields



class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ('password_hash',)
    bookings = fields.Nested('BookingSchema', many=True, exclude=('user',))

class TurfSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Turf
        load_instance = True

class GamingCenterSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = GamingCenter
        load_instance = True
    consoles = fields.Nested('ConsoleSchema', many=True, exclude=('gaming_center',))

class ConsoleSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Console
        load_instance = True
    slots = fields.Nested('SlotSchema', many=True, exclude=('console',))

class SlotSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Slot
        load_instance = True
    booking = fields.Nested('BookingSchema', exclude=('slot',), allow_none=True)

class BookingSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Booking
        load_instance = True
    user = fields.Nested(UserSchema, exclude=('bookings',))
    slot = fields.Nested(SlotSchema, exclude=('booking',))

user_schema = UserSchema()
turf_schema = TurfSchema()
gaming_center_schema = GamingCenterSchema()
console_schema = ConsoleSchema()
slot_schema = SlotSchema()
booking_schema = BookingSchema()