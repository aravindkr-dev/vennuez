import requests
from flask import Flask, request, jsonify , render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_restful import Api, Resource
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///booking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
api = Api(app)
CORS(app)  # Add this line

# MODELS
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_verified = db.Column(db.Boolean, default=True)  # Always True, no OTP
    is_admin = db.Column(db.Boolean, default=False)
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Turf(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)

class GamingCenter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    consoles = db.relationship('Console', backref='gaming_center', lazy=True)

class Console(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    gaming_center_id = db.Column(db.Integer, db.ForeignKey('gaming_center.id'), nullable=False)
    slots = db.relationship('Slot', backref='console', lazy=True)

class Slot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    console_id = db.Column(db.Integer, db.ForeignKey('console.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    is_booked = db.Column(db.Boolean, default=False)
    booking = db.relationship('Booking', backref='slot', uselist=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey('slot.id'), nullable=False)
    booking_time = db.Column(db.DateTime, default=datetime.utcnow)

# SCHEMAS
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

# RESOURCES
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

# ROUTE REGISTRATION
api.add_resource(SignupResource, '/signup')
api.add_resource(LoginResource, '/login')
api.add_resource(TurfResource, '/turfs')
api.add_resource(GamingCenterResource, '/gaming_centers')
api.add_resource(ConsoleResource, '/gaming_centers/<int:gc_id>/consoles')
api.add_resource(SlotResource, '/consoles/<int:console_id>/slots')
api.add_resource(BookSlotResource, '/slots/<int:slot_id>/book')





@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/creation')
def creation():
    return render_template('booking.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)