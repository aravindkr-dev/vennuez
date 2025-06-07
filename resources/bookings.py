from flask_restful import Resource, reqparse
from flask import jsonify
from models import db, Booking, Slot
from schemas import BookingSchema , SlotSchema
import random, qrcode

booking_schema = BookingSchema()
slot_schema = SlotSchema()

class CreateBooking(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        parser.add_argument('slot_id', type=int, required=True)
        args = parser.parse_args()

        slot = Slot.query.get(args['slot_id'])
        if not slot:
            return {'message': 'Slot not found'}, 404  # <-- Add this check before anything else

        if slot.is_booked:
            return {'message': 'Slot already booked'}, 400

        otp = str(random.randint(100000, 999999))
        qr = qrcode.make(f"Booking ID: {args['slot_id']} | OTP: {otp}")
        qr_path = f"static/qr_codes/booking_{args['user_id']}_{args['slot_id']}.png"
        qr.save(qr_path)

        booking = Booking(user_id=args['user_id'], slot_id=args['slot_id'], otp=otp, qr_path=qr_path)
        slot.is_booked = False

        db.session.add(booking)
        db.session.commit()

        return booking_schema.dump(booking)

class VerifyBooking(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('slot_id' , required = True)
        parser.add_argument('otp', required=True)
        args = parser.parse_args()

        booking = Booking.query.filter_by(otp=args['otp'], status='pending').first()
        slot = Slot.query.get(args["slot_id"])
        slot.is_booked = True
        if not booking:
            return {'message': 'Invalid or already verified OTP'}, 404

        booking.status = 'confirmed'
        db.session.commit()

        return {'message': 'Booking confirmed ✅'}

class BookingStatus(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('slot_id', type=int, required=False)
        parser.add_argument('user_id', type=int, required=False)
        args = parser.parse_args()

        if args['slot_id']:
            booking = Booking.query.get(args['slot_id'])
            if not booking:
                return {'message': 'Booking not found'}, 404
            return booking_schema.dump(booking), 200

        if args['user_id']:
            bookings = Booking.query.filter_by(user_id=args['user_id']).all()
            if not bookings:
                return {'message': 'No bookings found for this user'}, 404
            return booking_schema.dump(bookings, many=True), 200

        return {'message': 'Please provide booking_id or user_id as query parameter'}, 400

class CancelBooking(Resource):
    def patch(self):
        parser = reqparse.RequestParser()
        parser.add_argument('slot_id', type=int, required=False)
        parser.add_argument('user_id', type=int, required=False)
        args = parser.parse_args()

        if args['slot_id']:
            booking = Booking.query.get(args['slot_id'])
            if not booking:
                return {'message': 'Booking not found'}, 404

            slot = Slot.query.get(booking.slot_id)

            if slot:
                slot.is_booked = False

            db.session.delete(booking)
            db.session.commit()

            return booking_schema.dump(booking), 200

        return {'message': 'Please provide booking_id or user_id as query parameter'}, 400


class ShowSlots(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('slot_id', type=int, required=False) #-> slot_id
        #parser.add_argument('user_id', type=int, required=False)
        args = parser.parse_args()

        slot = Slot.query.get(args["slot_id"])

        return slot_schema.dump(slot)

