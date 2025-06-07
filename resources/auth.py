from flask_restful import Resource, reqparse
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from schemas import UserSchema

user_schema = UserSchema()

class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('phone', required=True)
        parser.add_argument('password', required=True)
        parser.add_argument('role', required=True)  # user or owner
        args = parser.parse_args()

        if User.query.filter_by(phone=args['phone']).first():
            return {'message': 'User already exists'}, 400

        hashed_password = generate_password_hash(args['password'])
        user = User(phone=args['phone'], password=hashed_password, role=args['role'])
        db.session.add(user)
        db.session.commit()

        return user_schema.dump(user), 201

class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('phone', required=True)
        parser.add_argument('password', required=True)
        args = parser.parse_args()

        user = User.query.filter_by(phone=args['phone']).first()
        if user and check_password_hash(user.password, args['password']):
            return {'message': 'Login successful ✅', 'user': user_schema.dump(user)}
        return {'message': 'Invalid credentials'}, 401