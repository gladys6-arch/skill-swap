# backend/routes/__init__.py

from .auth_routes import auth_bp
from .teacher_routes import teacher_bp
from .student_routes import student_bp
from .admin_routes import admin_bp
from .payment_routes import payment_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(payment_bp)
