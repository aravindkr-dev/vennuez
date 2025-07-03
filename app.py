import os
import logging
from flask import Flask, request, redirect, url_for, flash, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash
from flask_migrate import Migrate
from flask_login import LoginManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "D85*/#(fdsGFHGFh^65675&^576FDGFDt.[[;};=--=0-0)_-9089*&*^8hjhjggh")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize Flask-Login
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    from models import Owner, User
    from flask import session

    user_type = session.get('user_type')

    if user_type == 'owner':
        return Owner.query.get(int(user_id))
    elif user_type == 'user':
        return User.query.get(int(user_id))
    return None

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///gaming_center.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

migrate = Migrate(app, db)

from models import UserNotification  # adjust import path if needed

@app.before_request
def show_user_flash_notifications():
    if current_user.is_authenticated and hasattr(current_user, 'id'):
        notifs = UserNotification.query.filter_by(
            user_id=current_user.id,
            is_flash=True,
            is_read=False
        ).all()

        for notif in notifs:
            flash(notif.message, "info")
            notif.is_flash = False
            notif.is_read = True

        if notifs:
            db.session.commit()

with app.app_context():
    # Import models to ensure tables are created
    from models import *
    from routes import *

    # Create all tables
    db.create_all()