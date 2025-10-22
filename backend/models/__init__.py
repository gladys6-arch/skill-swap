from extensions import db

# Import all models so Flask-Migrate & SQLAlchemy are aware of them
from .user import User
from .course import Course, Module, Enrollment
from .payment import Payment
from .certificate import Certificate

# Optional: a function to initialize models (useful if you want to seed data later)
def init_models():
    db.create_all()
