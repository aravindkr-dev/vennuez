from flask_restful import Resource, reqparse
from models import Availability, db
from schemas import availability_schema, availabilities_schema
from datetime import datetime, timedelta
import math


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

class MarkAvailable(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        parser.add_argument('venue_id', type=int)
        parser.add_argument('sport', type=str)
        parser.add_argument('available_time', type=str)
        parser.add_argument('latitude', type=float, required=True)
        parser.add_argument('longitude', type=float, required=True)
        args = parser.parse_args()

        available = Availability(
            user_id=args['user_id'],
            venue_id=args['venue_id'],
            sport=args['sport'],
            available_time=datetime.strptime(args['available_time'], "%Y-%m-%d %H:%M:%S") if args['available_time'] else datetime.utcnow(),
            latitude=args['latitude'],
            longitude=args['longitude']
        )
        db.session.add(available)
        db.session.commit()

        return availability_schema.dump(available), 201


class FindFriends(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('latitude', type=float, required=True)
        parser.add_argument('longitude', type=float, required=True)
        parser.add_argument('sport', type=str)
        args = parser.parse_args()

        all_available = Availability.query.filter_by(is_active=True).all()
        results = []

        for friend in all_available:
            dist = haversine(args['latitude'], args['longitude'], friend.latitude, friend.longitude)
            if dist <= 10:
                if args['sport'] and args['sport'].lower() != friend.sport.lower():
                    continue
                results.append(friend)

        return availabilities_schema.dump(results), 200

