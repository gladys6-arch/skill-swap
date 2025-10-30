# routes/course_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Course, User, Payment

course_bp = Blueprint('course_bp', __name__)

# TEACHER: Add a new course
@course_bp.route('/teacher/add-course', methods=['POST'])
@jwt_required()
def add_course():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    if not user or user.role != 'teacher':
        return jsonify({'msg': 'Only teachers can add courses'}), 403

    data = request.get_json()
    new_course = Course(
        title=data['title'],
        description=data['description'],
        price=data['price'],
        link=data['link'],  # link to external learning website
        teacher_name=user.name,
        teacher_id=user.id
    )
    db.session.add(new_course)
    db.session.commit()

    return jsonify({'msg': 'Course added successfully'}), 201


# STUDENT: View all available courses
@course_bp.route('/student/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    result = [
        {
            'id': c.id,
            'title': c.title,
            'description': c.description,
            'price': c.price,
            'teacher_name': c.teacher_name
        }
        for c in courses
    ]
    return jsonify(result), 200


#  STUDENT: View a single course by ID
@course_bp.route('/student/course/<int:course_id>', methods=['GET'])
def get_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'msg': 'Course not found'}), 404

    return jsonify({
        'id': course.id,
        'title': course.title,
        'description': course.description,
        'price': course.price,
        'teacher_name': course.teacher_name
    }), 200


#  STUDENT: Access the external link (only after payment)
@course_bp.route('/student/course/<int:course_id>/access', methods=['GET'])
@jwt_required()
def access_course(course_id):
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    # Verify payment
    payment = Payment.query.filter_by(student_id=user.id, course_id=course_id, status='completed').first()
    if not payment:
        return jsonify({'msg': 'You must complete payment to access this course'}), 403

    course = Course.query.get(course_id)
    if not course:
        return jsonify({'msg': 'Course not found'}), 404

    return jsonify({'link': course.link}), 200
