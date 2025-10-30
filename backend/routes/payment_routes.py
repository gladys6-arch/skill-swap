# routes/payment_routes.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests, base64, datetime, json
from models import db, Payment, Course, User

payment_bp = Blueprint('payment_bp', __name__)

# Generate M-Pesa access token
def get_access_token():
    consumer_key = current_app.config['MPESA_CONSUMER_KEY']
    consumer_secret = current_app.config['MPESA_CONSUMER_SECRET']
    response = requests.get(
        "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
        auth=(consumer_key, consumer_secret)
    )
    return response.json().get('access_token')

# Initialize STK Push
@payment_bp.route('/initiate', methods=['POST'])
@jwt_required()
def initiate_payment():
    data = request.get_json()
    amount = data.get("amount")
    course_id = data.get("course_id")

    if not amount or not course_id:
        return jsonify({"msg": "Amount and course_id are required"}), 400

    # Get current student
    current_user_email = get_jwt_identity()
    student = User.query.filter_by(email=current_user_email).first()

    if not student or student.role != "student":
        return jsonify({"msg": "Unauthorized access"}), 403

    # Fetch course
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"msg": "Course not found"}), 404

    access_token = get_access_token()
    if not access_token:
        return jsonify({"msg": "Failed to generate M-Pesa token"}), 500

    # Prepare STK Push data
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    shortcode = current_app.config['MPESA_SHORTCODE']
    passkey = current_app.config['MPESA_PASSKEY']
    password = base64.b64encode((shortcode + passkey + timestamp).encode()).decode()

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": student.phone_number,  # you must store student phone number in your user model
        "PartyB": shortcode,
        "PhoneNumber": student.phone_number,
        "CallBackURL": current_app.config['CALLBACK_URL'],
        "AccountReference": f"Course_{course_id}",
        "TransactionDesc": f"Payment for {course.title}"
    }

    headers = {"Authorization": f"Bearer {access_token}"}
    res = requests.post(
        "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers=headers
    )

    # Store payment in DB
    payment_data = res.json()
    new_payment = Payment(
        student_id=student.id,
        course_id=course.id,
        amount=amount,
        status="Pending"
    )
    db.session.add(new_payment)
    db.session.commit()

    return jsonify({
        "msg": "STK Push initiated. Check your phone to complete the payment.",
        "response": payment_data
    }), 200


# Callback from Safaricom (after payment)
@payment_bp.route('/callback', methods=['POST'])
def payment_callback():
    data = request.get_json()
    print("M-PESA CALLBACK:", json.dumps(data, indent=4))

    try:
        body = data.get("Body", {})
        stk_callback = body.get("stkCallback", {})

        result_code = stk_callback.get("ResultCode")
        merchant_request_id = stk_callback.get("MerchantRequestID")

        # Only process successful payments
        if result_code == 0:
            callback_metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
            mpesa_code = next((item["Value"] for item in callback_metadata if item["Name"] == "MpesaReceiptNumber"), None)
            amount = next((item["Value"] for item in callback_metadata if item["Name"] == "Amount"), None)
            phone = next((item["Value"] for item in callback_metadata if item["Name"] == "PhoneNumber"), None)

            # Find payment record by student phone + pending status
            from models import Payment, User
            student = User.query.filter_by(phone_number=phone).first()
            if student:
                payment = Payment.query.filter_by(student_id=student.id, status="Pending").order_by(Payment.date.desc()).first()
                if payment:
                    payment.status = "Paid"
                    db.session.commit()
                    print(f"Payment successful: {mpesa_code}")

        return jsonify({"ResultCode": 0, "ResultDesc": "Payment processed successfully"})
    except Exception as e:
        print("Error processing callback:", e)
        return jsonify({"ResultCode": 1, "ResultDesc": "Callback error"})
    
@payment_bp.route('/status/<int:course_id>', methods=['GET'])
@jwt_required()
def check_payment_status(course_id):
    current_user_email = get_jwt_identity()
    from models import User
    student = User.query.filter_by(email=current_user_email).first()

    if not student:
        return jsonify({"msg": "User not found"}), 404

    payment = Payment.query.filter_by(student_id=student.id, course_id=course_id, status="Paid").first()
    if payment:
        return jsonify({"paid": True})
    return jsonify({"paid": False})


