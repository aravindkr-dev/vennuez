import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

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
    import models
    import routes

    # Create all tables
    db.create_all()

    # Add some default data if tables are empty
    if models.Owner.query.count() == 0:
        logging.info("Creating default admin user...")
        from werkzeug.security import generate_password_hash

        admin = models.Owner(
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

        if __name__ == '__main__':
            app.run(debug=True, host='0.0.0.0', port=5000)
