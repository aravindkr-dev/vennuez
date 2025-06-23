import sys
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from app import app, db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

def run_migrations():
    try:
        with app.app_context():
            logger.info('Starting database initialization...')
            
            # Import models
            from models import TimeSlot
            
            # Initialize database
            db.create_all()
            logger.info('Database tables created successfully')
            
            # Run migrations
            from flask_migrate import upgrade as _upgrade
            _upgrade()
            logger.info('Migration completed successfully!')
            return True
    except SQLAlchemyError as e:
        logger.error(f'Database error occurred: {str(e)}')
        return False
    except Exception as e:
        logger.error(f'An unexpected error occurred: {str(e)}')
        return False

if __name__ == '__main__':
    success = run_migrations()
    sys.exit(0 if success else 1)