from flask_restful import Resource, reqparse
from models import db, Venue, Slot
from schemas import VenueSchema
from datetime import datetime

venue_schema = VenueSchema()
venue_list_schema = VenueSchema(many=True)

class VenueList(Resource):
    def get(self):
        venues = Venue.query.all()
        return venue_list_schema.dump(venues)

class CreateVenue(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('owner_id', type=int, required=True)
        parser.add_argument('name', required=True)
        parser.add_argument('location', required=True)
        parser.add_argument('description', required=True)
        parser.add_argument('sport_type', required=True)
        args = parser.parse_args()

        venue = Venue(**args)
        db.session.add(venue)
        db.session.commit()
        return venue_schema.dump(venue)

class VenueSlots(Resource):
    def get(self, venue_id):
        venue = Venue.query.get_or_404(venue_id)
        return {'slots': [{'id': s.id, 'date': s.date.isoformat(), 'start': s.start_time.isoformat(), 'end': s.end_time.isoformat(), 'is_booked': s.is_booked} for s in venue.slot_set]}