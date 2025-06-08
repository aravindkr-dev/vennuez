from app import db
from datetime import datetime
import uuid


class Owner(db.Model):
    __tablename__ = 'owners'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    gaming_center_name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    consoles = db.relationship('Console', backref='owner', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Owner {self.username}>'


class Console(db.Model):
    __tablename__ = 'consoles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    console_type = db.Column(db.String(50), nullable=False)  # PS5, PS4, Xbox, PC, etc.
    hourly_rate = db.Column(db.Float, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign Key
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'), nullable=False)

    # Relationships
    slots = db.relationship('TimeSlot', backref='console', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Console {self.name}>'


class TimeSlot(db.Model):
    __tablename__ = 'time_slots'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    advance_paid = db.Column(db.Float, default=50.0)  # Fixed advance amount
    is_booked = db.Column(db.Boolean, default=False)

    # Booking details
    booking_id = db.Column(db.String(20), unique=True, nullable=True)
    customer_name = db.Column(db.String(100), nullable=True)
    customer_phone = db.Column(db.String(20), nullable=True)
    customer_email = db.Column(db.String(120), nullable=True)
    customer_age = db.Column(db.Integer, nullable=True)
    special_requests = db.Column(db.Text, nullable=True)

    # Contact preferences
    contact_sms = db.Column(db.Boolean, default=True)
    contact_whatsapp = db.Column(db.Boolean, default=True)
    contact_email = db.Column(db.Boolean, default=False)

    # Payment status
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed
    payment_id = db.Column(db.String(100), nullable=True)

    booking_time = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign Key
    console_id = db.Column(db.Integer, db.ForeignKey('consoles.id'), nullable=False)

    def generate_booking_id(self):
        """Generate a unique booking ID"""
        return f"GC{str(uuid.uuid4())[:8].upper()}"

    def calculate_total_amount(self):
        """Calculate total amount based on duration and hourly rate"""
        if self.start_time and self.end_time and self.console:
            duration_hours = (self.end_time - self.start_time).total_seconds() / 3600
            return duration_hours * self.console.hourly_rate
        return 0

    def __repr__(self):
        return f'<TimeSlot {self.booking_id or self.id}>'


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'
