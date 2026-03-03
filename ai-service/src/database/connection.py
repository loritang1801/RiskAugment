from flask_sqlalchemy import SQLAlchemy
import logging

logger = logging.getLogger(__name__)

db = SQLAlchemy()


def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    
    with app.app_context():
        try:
            # Ensure models are imported before create_all so metadata is complete.
            from src.database import models  # noqa: F401
            # Create all tables
            db.create_all()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise


def get_db_session():
    """Get current database session"""
    return db.session
