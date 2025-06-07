from flask_restful import Resource, reqparse
from models import User, db, TurfOwner , GamingCenterOwner
from schemas import UserSchema , TurfOwnerSchema , GamingCenterOwnerSchema


user_schema = UserSchema()


class CreateNewUser(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('phone', type=str, required=True)
        parser.add_argument('role', type=str, required=True)
        args = parser.parse_args()

        user = User.query.filter_by(phone=args["phone"]).first()

        if not user:
            new_user = User(name=args["name"] , phone=args["phone"] , role=args["role"])
            db.session.add(new_user)
            db.session.commit()
            return user_schema.dump(new_user) , 201

        return {"message":"User Already Exist"} , 409


class CreateNewTurfOwner(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('phone', type=str, required=True)
        """parser.add_argument('latitude', type=float, required=True)
        parser.add_argument('longitude', type=float, required=True)
        parser.add_argument('map', type=str, required=True)"""
        args = parser.parse_args()

        turf_owner_schema = TurfOwnerSchema()
        turf_owner = TurfOwner.query.filter_by(phone=args["phone"]).first()

        if not turf_owner:
            owner = TurfOwner(name = args["name"] , phone = args["phone"])
            db.session.add(owner)
            db.session.commit()
            return turf_owner_schema.dump(owner) , 201

        return {"message": "Turf Owner Already Exist"}, 409



class CreateNewGamingCenterOwner(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('phone', type=str, required=True)
        """parser.add_argument('latitude', type=float, required=True)
        parser.add_argument('longitude', type=float, required=True)
        parser.add_argument('map', type=str, required=True)"""
        args = parser.parse_args()

        gaming_center_owner_schema = GamingCenterOwnerSchema()
        turf_owner = GamingCenterOwner.query.filter_by(phone=args["phone"]).first()

        if not turf_owner:
            owner = GamingCenterOwner(name = args["name"] , phone = args["phone"])
            db.session.add(owner)
            db.session.commit()
            return gaming_center_owner_schema.dump(owner) , 201

        return {"message": "Turf Owner Already Exist"}, 409
