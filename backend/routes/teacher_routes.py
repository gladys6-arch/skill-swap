from flask import Blueprint, request, jsonify
from extensions import db
from models.course import Course, Module
from models.user import User        # Add this import
from models.payment import Payment  # Add this import
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.decorators import role_required

teacher_bp = Blueprint('teacher_bp', __name__)

@teacher_bp.route('/teacher/add-skill', methods=['POST'])
@jwt_required()
@role_required('teacher')
def add_skill():
    user = get_jwt_identity()
    data = request.get_json()
    course = Course(title=data['title'], description=data['description'], price=data['price'], teacher_id=user['id'])
    db.session.add(course)
    db.session.commit()
    return jsonify({"msg": "Course added successfully"})

@teacher_bp.route('/course/<int:course_id>/add-link', methods=['PUT'])
@jwt_required()
@role_required('teacher')
def add_course_link(course_id):
    data = request.get_json()
    course_link = data.get("course_link")

    teacher_email = get_jwt_identity()
    teacher = User.query.filter_by(email=teacher_email).first()

    course = Course.query.get(course_id)
    if not course or course.teacher_id != teacher.id:
        return jsonify({"msg": "Course not found or unauthorized"}), 404

    course.course_link = course_link
    db.session.commit()
    return jsonify({"msg": "Course link added successfully"})

@teacher_bp.route('/course/<int:course_id>/students', methods=['GET'])
@jwt_required()
@role_required('teacher')
def view_course_students(course_id):
    teacher_email = get_jwt_identity()
    teacher = User.query.filter_by(email=teacher_email).first()

    course = Course.query.get(course_id)
    if not course or course.teacher_id != teacher.id:
        return jsonify({"msg": "Course not found or unauthorized"}), 404

    payments = Payment.query.filter_by(course_id=course_id, status="Paid").all()
    students = [
        {"name": p.student.name, "email": p.student.email, "amount": p.amount}
        for p in payments
    ]
    return jsonify(students)
