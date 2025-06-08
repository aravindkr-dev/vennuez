from flask import Flask, request, jsonify , render_template
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

from models import *
from flask_restful import Api, Resource
from schemas import *
from datetime import datetime


class SignupResource(Resource):
    def post(self):
        data = request.get_json()
        if User.query.filter((User.username == data['username']) | (User.phone_number == data['phone_number'])).first():
            return {'msg': 'User already exists'}, 400
        user = User(
            username=data['username'],
            phone_number=data['phone_number'],
            is_verified=True,# Always True, no OTP
            is_admin = data['is_admin']
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return user_schema.dump(user), 201

class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        phone_number = data['phone_number']
        password = data['password']
        user = User.query.filter_by(phone_number=phone_number, is_verified=True).first()
        if not user or not user.check_password(password):
            return {'msg': 'Invalid credentials'}, 401
        access_token = create_access_token(identity=str(user.id))
        return {'access_token': access_token}

class TurfResource(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user.is_admin:
            return {'msg': 'Admins only'}, 403
        data = request.get_json()
        turf = Turf(
            name=data['name'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            description=data.get('description', '')
        )
        db.session.add(turf)
        db.session.commit()
        return turf_schema.dump(turf), 201

class GamingCenterResource(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user.is_admin:
            return {'msg': 'Admins only'}, 403
        data = request.get_json()
        gc = GamingCenter(
            name=data['name'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            description=data.get('description', '')
        )
        db.session.add(gc)
        db.session.commit()
        return gaming_center_schema.dump(gc), 201

class ConsoleResource(Resource):
    @jwt_required()
    def post(self, gc_id):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user.is_admin:
            return {'msg': 'Admins only'}, 403
        data = request.get_json()
        console = Console(name=data['name'], gaming_center_id=gc_id)
        db.session.add(console)
        db.session.commit()
        return console_schema.dump(console), 201

class SlotResource(Resource):
    @jwt_required()
    def post(self, console_id):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user.is_admin:
            return {'msg': 'Admins only'}, 403
        data = request.get_json()
        start_time = datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M')
        end_time = datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M')
        slot = Slot(console_id=console_id, start_time=start_time, end_time=end_time)
        db.session.add(slot)
        db.session.commit()
        return slot_schema.dump(slot), 201

    def get(self, console_id):
        slots = Slot.query.filter_by(console_id=console_id, is_booked=False).all()
        return slot_schema.dump(slots, many=True), 200

class BookSlotResource(Resource):
    @jwt_required()
    def post(self, slot_id):
        user_id = get_jwt_identity()
        slot = Slot.query.get(slot_id)
        if not slot or slot.is_booked:
            return {'msg': 'Slot not available'}, 400
        booking = Booking(user_id=user_id, slot_id=slot_id)
        slot.is_booked = True
        db.session.add(booking)
        db.session.commit()
        return booking_schema.dump(booking), 201