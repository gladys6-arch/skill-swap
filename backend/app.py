from flask import Flask
from config import Config
from extensions import db, migrate, jwt, cors
from routes.auth_routes import auth_bp
from routes.teacher_routes import teacher_bp
from routes.student_routes import student_bp
from routes.admin_routes import admin_bp
from routes.payment_routes import payment_bp
from models import user, course, payment, certificate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(payment_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
