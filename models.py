from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time

db = SQLAlchemy()

# =================== USER MODEL ===================

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # user / owner

    #turf_owner = db.relationship('TurfOwner', backref='user', uselist=False)
    #gaming_owner = db.relationship('GamingCenterOwner', backref='user', uselist=False)


# =================== TURF SECTION ===================

class TurfOwner(db.Model):
    __tablename__ = 'turf_owners'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)

    turfs = db.relationship('Turf', backref='owner', cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Turf(db.Model):
    __tablename__ = 'turfs'
    id = db.Column(db.Integer, primary_key=True)
    turf_owner_id = db.Column(db.Integer, db.ForeignKey('turf_owners.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    map = db.Column(db.String(1000), nullable=False)
    sport_type = db.Column(db.String(1000), nullable=False)
    description = db.Column(db.Text)
    price_per_hour = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    images = db.relationship('TurfImage', backref='turf', cascade='all, delete-orphan')
    amenities = db.relationship('TurfAmenity', backref='turf', cascade='all, delete-orphan')
    slots = db.relationship('TurfSlot', backref='turf', cascade='all, delete-orphan')


class TurfImage(db.Model):
    __tablename__ = 'turf_images'
    id = db.Column(db.Integer, primary_key=True)
    turf_id = db.Column(db.Integer, db.ForeignKey('turfs.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class TurfAmenity(db.Model):
    __tablename__ = 'turf_amenities'
    id = db.Column(db.Integer, primary_key=True)
    turf_id = db.Column(db.Integer, db.ForeignKey('turfs.id'), nullable=False)
    amenity_name = db.Column(db.String(100), nullable=False)


class TurfSlot(db.Model):
    __tablename__ = 'turf_slots'
    id = db.Column(db.Integer, primary_key=True)
    turf_id = db.Column(db.Integer, db.ForeignKey('turfs.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_booked = db.Column(db.Boolean, default=False)
    price = db.Column(db.Float, nullable=False)

    bookings = db.relationship('TurfBooking', backref='slot', cascade='all, delete-orphan')


class TurfBooking(db.Model):
    __tablename__ = 'turf_bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    turf_slot_id = db.Column(db.Integer, db.ForeignKey('turf_slots.id'), nullable=False)
    otp = db.Column(db.String(6))
    qr_path = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')
    payment_status = db.Column(db.String(20), default='pending')
    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# =================== GAMING SECTION ===================

class GamingCenterOwner(db.Model):
    __tablename__ = 'gaming_center_owners'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)

    gaming_centers = db.relationship('GamingCenter', backref='owner', cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GamingCenter(db.Model):
    __tablename__ = 'gaming_centers'
    id = db.Column(db.Integer, primary_key=True)
    gaming_center_owner_id = db.Column(db.Integer, db.ForeignKey('gaming_center_owners.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    map = db.Column(db.String(1000), nullable=False)

    images = db.relationship('GamingCenterImage', backref='gaming_center', cascade='all, delete-orphan')
    amenities = db.relationship('GamingCenterAmenity', backref='gaming_center', cascade='all, delete-orphan')
    consoles = db.relationship('Console', backref='gaming_center', cascade='all, delete-orphan')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class GamingCenterImage(db.Model):
    __tablename__ = 'gaming_center_images'
    id = db.Column(db.Integer, primary_key=True)
    gaming_center_id = db.Column(db.Integer, db.ForeignKey('gaming_centers.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class GamingCenterAmenity(db.Model):
    __tablename__ = 'gaming_center_amenities'
    id = db.Column(db.Integer, primary_key=True)
    gaming_center_id = db.Column(db.Integer, db.ForeignKey('gaming_centers.id'), nullable=False)
    amenity_name = db.Column(db.String(100), nullable=False)


class Console(db.Model):
    __tablename__ = 'consoles'
    id = db.Column(db.Integer, primary_key=True)
    gaming_center_id = db.Column(db.Integer, db.ForeignKey('gaming_centers.id'), nullable=False)
    console_type = db.Column(db.String(50), nullable=False)
    console_name = db.Column(db.String(100), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    max_players = db.Column(db.Integer, default=1)

    slots = db.relationship('ConsoleSlot', backref='console', cascade='all, delete-orphan')
    games = db.relationship('ConsoleGame', backref='console', cascade='all, delete-orphan')


class ConsoleGame(db.Model):
    __tablename__ = 'console_games'
    id = db.Column(db.Integer, primary_key=True)
    console_id = db.Column(db.Integer, db.ForeignKey('consoles.id'), nullable=False)
    game_name = db.Column(db.String(100), nullable=False)
    game_genre = db.Column(db.String(50))
    is_multiplayer = db.Column(db.Boolean, default=False)


class ConsoleSlot(db.Model):
    __tablename__ = 'console_slots'
    id = db.Column(db.Integer, primary_key=True)
    console_id = db.Column(db.Integer, db.ForeignKey('consoles.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_booked = db.Column(db.Boolean, default=False)
    price = db.Column(db.Float, nullable=False)

    bookings = db.relationship('GamingBooking', backref='slot', cascade='all, delete-orphan')


class GamingBooking(db.Model):
    __tablename__ = 'gaming_bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    console_slot_id = db.Column(db.Integer, db.ForeignKey('console_slots.id'), nullable=False)
    players_count = db.Column(db.Integer, default=1)
    selected_games = db.Column(db.Text)  # JSON or comma-separated game names
    otp = db.Column(db.String(6))
    qr_path = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')
    payment_status = db.Column(db.String(20), default='pending')
    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
