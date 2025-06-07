from flask_restful import Resource, reqparse
from models import User , db
from schemas import UserSchema


user_schema = UserSchema()

class LoginUser(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('phone', type=str, required=True)
        args = parser.parse_args()

        user = User.query.filter_by(phone = args["phone"]).first()

        if user:
            return user_schema.dump(user)

        return {"message":"User Doesn't Exist"}