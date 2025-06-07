from flask_restful import Resource, reqparse
from models import User , db
from schemas import UserSchema


user_schema = UserSchema()

class FindUser(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=False)
        parser.add_argument('phone', type=str, required=False)
        args = parser.parse_args()

        user = None
        if args["name"]:
            user = User.query.filter_by(name=args["name"]).first()
        if args["phone"]:
            user = User.query.filter_by(phone=args["phone"]).first()

        if user:
            return user_schema.dump(user)

        return {"message":"User Not Found"}


class DeleteUsers(Resource):
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('phone', type=str, required=True)
        args = parser.parse_args()

        user = User.query.filter_by(phone=args["phone"]).first()

        if user:
            db.session.delete(user)
            db.session.commit()
            return user_schema.dump(user)

        return {"message":"User Not Found"}