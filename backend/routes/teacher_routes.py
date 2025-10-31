from flask import Blueprint, request, jsonify
from extensions import db
from models.course import Course
from models.user import User
from models.payment import Payment
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.decorators import role_required

teacher_bp = Blueprint('teacher_bp', __name__)

# -----------------------------
# Add new skill / course
# -----------------------------
@teacher_bp.route('/teacher/add-skill', methods=['POST'])
@jwt_required()
@role_required('teacher')
def add_skill():
    teacher_email = get_jwt_identity()
    teacher = User.query.filter_by(email=teacher_email).first()

    if not teacher:
        return jsonify({"msg": "Teacher not found"}), 404

    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    price = data.get('price')
    course_link = data.get('course_link')  # optional external link (YouTube, Google Drive, etc.)

    if not title or not description or not price:
        return jsonify({"msg": "Missing required fields"}), 400

    new_course = Course(
        title=title,
        description=description,
        price=price,
        teacher_id=teacher.id,
        teacher_name=teacher.name,
        course_link=data.get('course_link') 
    )
    db.session.add(new_course)
    db.session.commit()

    return jsonify({"msg": "Course added successfully"}), 201


# -----------------------------
# View students in a course
# -----------------------------
@teacher_bp.route('/course/<int:course_id>/students', methods=['GET'])
@jwt_required()
@role_required('teacher')
def view_course_students(course_id):
    teacher_email = get_jwt_identity()
    teacher = User.query.filter_by(email=teacher_email).first()

    if not teacher:
        return jsonify({"msg": "Teacher not found"}), 404

    course = Course.query.get(course_id)
    if not course or course.teacher_id != teacher.id:
        return jsonify({"msg": "Course not found or unauthorized"}), 404

    payments = Payment.query.filter_by(course_id=course_id, status="Paid").all()

    students = [
        {
            "name": p.student.name,
            "email": p.student.email,
            "amount": p.amount,
            "paid_on": p.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for p in payments
    ]

    return jsonify({
        "course_title": course.title,
        "students": students
    })


# -----------------------------
# Teacher's course summary / balance
# -----------------------------
@teacher_bp.route('/teacher/summary', methods=['GET'])
@jwt_required()
@role_required('teacher')
def teacher_summary():
    teacher_email = get_jwt_identity()
    teacher = User.query.filter_by(email=teacher_email).first()

    if not teacher:
        return jsonify({"msg": "Teacher not found"}), 404

    payments = Payment.query.filter_by(teacher_id=teacher.id, status="Paid").all()
    total_earnings = sum(p.teacher_share for p in payments)

    return jsonify({
        "teacher_name": teacher.name,
        "total_courses": Course.query.filter_by(teacher_id=teacher.id).count(),
        "total_students": len({p.student_id for p in payments}),
        "total_earnings": total_earnings
    })
