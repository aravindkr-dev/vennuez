from app import db
from datetime import datetime
import uuid
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Owner(UserMixin, db.Model):
    __tablename__ = 'owners'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    gaming_center_name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    google_maps_link = db.Column(db.String(500), nullable=True)
    amenities = db.Column(db.Text, nullable=True)  # Stored as JSON string
    venue_image1 = db.Column(db.String(500), nullable=True)
    venue_image2 = db.Column(db.String(500), nullable=True)
    venue_image3 = db.Column(db.String(500), nullable=True)
    venue_image4 = db.Column(db.String(500), nullable=True)
    images_uploaded = db.Column(db.Boolean, default=False)

    # Relationships
    consoles = db.relationship('Console', backref='owner', lazy=True, cascade='all, delete-orphan')
    subscriptions = db.relationship("Subscription", back_populates="owner", cascade="all, delete")

    def __repr__(self):
        return f'<Owner {self.username}>'


class Console(db.Model):
    __tablename__ = 'consoles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    console_type = db.Column(db.String(50), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)  # Rate per person per hour
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign Keys
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
    advance_paid = db.Column(db.Float, default=0.0)  # Fixed advance amount
    is_booked = db.Column(db.Boolean, default=False)
    snacks_amount = db.Column(db.Float, default=0.0)
    final_amount = db.Column(db.Float, default=0.0)
    completed = db.Column(db.Boolean, default=False)
    number_of_people = db.Column(db.Integer, default=1)  # New field for number of people

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

    # Foreign Keys
    console_id = db.Column(db.Integer, db.ForeignKey('consoles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Optional for unregistered bookings

    def generate_booking_id(self):
        """Generate a unique booking ID"""
        return f"GC{str(uuid.uuid4())[:8].upper()}"

    def calculate_total_amount(self):
        """Calculate total amount based on duration, hourly rate, and number of people"""
        if self.start_time and self.end_time:
            console = Console.query.get(self.console_id)
            if console:
                duration_hours = (self.end_time - self.start_time).total_seconds() / 3600
                return duration_hours * console.hourly_rate * self.number_of_people
        return 0

    def __repr__(self):
        return f'<TimeSlot {self.booking_id or self.id}>'


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=False , unique = True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_spent = db.Column(db.Float, default=0.0)

    # Relationships
    bookings = db.relationship('TimeSlot', backref='user', lazy=True, foreign_keys='TimeSlot.user_id')
    coin_balances = db.relationship('UserCoinBalance', backref='user', lazy=True)
    subscriptions = db.relationship("Subscription", back_populates="user", cascade="all, delete")

    def set_password(self, password):
        """Set the user's password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)

    def get_coin_balance(self, gaming_center_name):
        """Get user's coin balance for a specific gaming center"""
        balance = UserCoinBalance.query.filter_by(
            user_id=self.id,
            gaming_center_name=gaming_center_name
        ).first()
        return balance.coins if balance else 0

    def __repr__(self):
        return f'<User {self.username}>'


class UserCoinBalance(db.Model):
    __tablename__ = 'user_coin_balances'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    gaming_center_name = db.Column(db.String(200), nullable=False)
    coins = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'gaming_center_name'),)

    def __repr__(self):
        return f'<UserCoinBalance {self.user_id}:{self.gaming_center_name}:{self.coins}>'


class CoinTransaction(db.Model):
    __tablename__ = 'coin_transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'), nullable=False)
    gaming_center_name = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # Positive for add, negative for deduct
    transaction_type = db.Column(db.String(50), nullable=False)  # 'purchase', 'booking', 'refund'
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='coin_transactions')
    owner = db.relationship('Owner', backref='coin_transactions')

    def __repr__(self):
        return f'<CoinTransaction {self.transaction_type}:{self.amount}>'


class Snack(db.Model):
    __tablename__ = 'snacks'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    rate = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Snack {self.name}>'


class ConsolePricingTier(db.Model):
    __tablename__ = 'console_pricing_tiers'

    id = db.Column(db.Integer, primary_key=True)
    console_id = db.Column(db.Integer, db.ForeignKey('consoles.id'), nullable=False)
    max_people = db.Column(db.Integer, nullable=False)
    rate_per_person = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<ConsolePricingTier {self.console_id}:up to {self.max_people}:{self.rate_per_person}>'



class Subscription(db.Model):
    __tablename__ = "subscription"
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="subscriptions")
    owner = db.relationship("Owner", back_populates="subscriptions")




class UsedToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(512), unique=True, nullable=False)
    used_at = db.Column(db.DateTime, default=datetime.utcnow)
