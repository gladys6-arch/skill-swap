from flask import Flask
from flask_cors import CORS
from extensions import db, jwt
from config import Config
from dotenv import load_dotenv
import os

load_dotenv()  # this reads .env file

MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
MPESA_PASSKEY = os.getenv("MPESA_PASSKEY")
MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE")



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)

    from routes.auth_routes import auth_bp
    from routes.admin_routes import admin_bp
    from routes.teacher_routes import teacher_bp
    from routes.student_routes import student_bp
    from routes.payment_routes import payment_bp
    from routes.course_routes import course_bp 



    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(teacher_bp, url_prefix='/api/teacher')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(payment_bp, url_prefix='/api/payment')
    app.register_blueprint(course_bp, url_prefix='/api/courses')

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)