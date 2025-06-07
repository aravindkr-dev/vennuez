from flask_marshmallow import Marshmallow
from models import *

ma = Marshmallow()

"""class BookingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Booking
        load_instance = True

class SlotSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Slot
        load_instance = True"""

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True

"""class VenueSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Venue
        load_instance = True


class AvailabilitySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Availability
        load_instance = True

availability_schema = AvailabilitySchema()
availabilities_schema = AvailabilitySchema(many=True)"""


class TurfOwnerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TurfOwner
        load_instance = True


class GamingCenterOwnerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = GamingCenterOwner
        load_instance = True