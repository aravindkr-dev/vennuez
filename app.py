import os
import logging
from flask import Flask, request, redirect, url_for, flash, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash

# Configure logging
logging.basicConfig(level=logging.DEBUG)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///gaming_center.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models to ensure tables are created
    from models import Owner, Console, TimeSlot, User
    import routes

    # Create all tables
    db.create_all()

    # Add some default data if tables are empty
    if Owner.query.count() == 0:
        logging.info("Creating default admin user...")
        admin = Owner(
            username="admin",
            email="admin@gamingcenter.com",
            password_hash=generate_password_hash("admin123"),
            phone="9876543210",
            gaming_center_name="Demo Gaming Center",
            address="123 Gaming Street, Tech City, TC 12345"
        )
        db.session.add(admin)
        db.session.commit()
        logging.info("Default admin user created (username: admin, password: admin123)")

@app.route('/register', methods=['GET', 'POST'])
def user_signup():
    if request.method == 'POST':
        username = request.form.get('username', '')  # Default to empty string if missing
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        phone = request.form.get('phone', '')
        role = request.form.get('role', 'user')
        
        if not all([username, email, password, confirm_password, phone]):
            flash('All fields are required', 'danger')
            return redirect(url_for('user_signup'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('user_signup'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('user_signup'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password, phone=phone, role=role)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')
