# routes/payment_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Payment, Course, User
from utils.decorators import role_required
from datetime import datetime
import os, base64, requests

payment_bp = Blueprint("payment_bp", __name__)

# --- Helper functions (now inline) ---
def get_access_token():
    consumer_key = os.getenv("MPESA_CONSUMER_KEY")
    consumer_secret = os.getenv("MPESA_CONSUMER_SECRET")

    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(consumer_key, consumer_secret))
    return response.json().get("access_token")

def generate_password():
    shortcode = os.getenv("MPESA_SHORTCODE")
    passkey = os.getenv("MPESA_PASSKEY")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()
    return password, timestamp


# --- Basic info route ---
@payment_bp.route("/", methods=["GET"])
def payment_info():
    return jsonify({
        "message": "SkillHub Payment API",
        "endpoints": {
            "process": "POST /api/payment/process",
            "callback": "POST /api/payment/callback",
            "student_history": "GET /api/payment/history",
            "teacher_earnings": "GET /api/payment/teacher-earnings",
            "admin_summary": "GET /api/payment/admin-summary",
        },
        "status": "active"
    })


# --- Student initiates M-Pesa payment ---
@payment_bp.route("/process", methods=["POST"])
@jwt_required()
@role_required("student")
def process_payment():
    data = request.get_json()
    student_email = get_jwt_identity()
    student = User.query.filter_by(email=student_email).first()

    if not student:
        return jsonify({"msg": "Student not found"}), 404

    course = Course.query.get(data.get("course_id"))
    if not course:
        return jsonify({"msg": "Course not found"}), 404

    amount = float(data.get("amount", 0))
    if amount <= 0:
        return jsonify({"msg": "Invalid amount"}), 400

    access_token = get_access_token()
    password, timestamp = generate_password()

    payload = {
        "BusinessShortCode": os.getenv("MPESA_SHORTCODE"),
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": student.phone_number,  # ensure you have this field in User
        "PartyB": os.getenv("MPESA_SHORTCODE"),
        "PhoneNumber": student.phone_number,
        "CallBackURL": os.getenv("MPESA_CALLBACK_URL"),
        "AccountReference": f"COURSE-{course.id}",
        "TransactionDesc": f"Payment for {course.title}"
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
        headers=headers,
        json=payload
    )

    result = response.json()

    # Save initial payment info
    teacher = course.teacher
    payment = Payment(
        student_id=student.id,
        teacher_id=teacher.id,
        course_id=course.id,
        amount=amount,
        teacher_share=round(amount * 0.8, 2),
        admin_share=round(amount * 0.2, 2),
        status="Pending",
        transaction_id=result.get("CheckoutRequestID")
    )
    db.session.add(payment)
    db.session.commit()

    return jsonify({
        "msg": "M-Pesa STK Push initiated.",
        "checkout_id": result.get("CheckoutRequestID"),
        "response": result
    }), 200


# --- M-Pesa callback route ---
@payment_bp.route("/callback", methods=["POST"])
def payment_callback():
    data = request.get_json()
    stk_callback = data.get("Body", {}).get("stkCallback", {})
    checkout_id = stk_callback.get("CheckoutRequestID")
    result_code = stk_callback.get("ResultCode")

    payment = Payment.query.filter_by(transaction_id=checkout_id).first()
    if not payment:
        return jsonify({"msg": "Payment not found"}), 404

    if result_code == 0:
        payment.status = "Completed"
    else:
        payment.status = "Failed"

    db.session.commit()

    return jsonify({"msg": "Callback processed successfully"}), 200


# --- Student views payment history ---
@payment_bp.route("/history", methods=["GET"])
@jwt_required()
@role_required("student")
def payment_history():
    student_email = get_jwt_identity()
    student = User.query.filter_by(email=student_email).first()
    if not student:
        return jsonify({"msg": "Student not found"}), 404

    payments = Payment.query.filter_by(student_id=student.id).all()
    return jsonify([
        {
            "id": p.id,
            "course_id": p.course_id,
            "amount": p.amount,
            "status": p.status,
            "date": p.timestamp.strftime("%Y-%m-%d %H:%M")
        } for p in payments
    ]), 200


# --- Teacher views their earnings ---
@payment_bp.route("/teacher-earnings", methods=["GET"])
@jwt_required()
@role_required("teacher")
def teacher_earnings():
    teacher_email = get_jwt_identity()
    teacher = User.query.filter_by(email=teacher_email).first()
    if not teacher:
        return jsonify({"msg": "Teacher not found"}), 404

    payments = Payment.query.filter_by(teacher_id=teacher.id, status="Completed").all()
    total_earned = sum(p.teacher_share for p in payments)
    unpaid = sum(p.teacher_share for p in payments if not p.teacher_paid)

    return jsonify({
        "teacher": teacher.name,
        "total_earned": total_earned,
        "unpaid_balance": unpaid,
        "payments": [
            {
                "course_id": p.course_id,
                "amount": p.amount,
                "teacher_share": p.teacher_share,
                "paid": p.teacher_paid,
                "date": p.timestamp.strftime("%Y-%m-%d %H:%M")
            } for p in payments
        ]
    }), 200


# --- Admin summary and teacher payout ---
@payment_bp.route("/admin-summary", methods=["GET"])
@jwt_required()
@role_required("admin")
def admin_summary():
    payments = Payment.query.filter_by(status="Completed").all()
    total_collected = sum(p.amount for p in payments)
    total_teacher_share = sum(p.teacher_share for p in payments)
    total_admin_share = sum(p.admin_share for p in payments)

    return jsonify({
        "total_collected": total_collected,
        "total_teacher_share": total_teacher_share,
        "total_admin_share": total_admin_share,
        "payments_count": len(payments)
    }), 200


# --- Admin marks teacher payout as complete ---
@payment_bp.route("/mark-paid/<int:payment_id>", methods=["PUT"])
@jwt_required()
@role_required("admin")
def mark_teacher_paid(payment_id):
    payment = Payment.query.get(payment_id)
    if not payment:
        return jsonify({"msg": "Payment not found"}), 404

    payment.teacher_paid = True
    db.session.commit()

    return jsonify({"msg": f"Teacher payment marked as complete for Payment ID {payment_id}"}), 200
