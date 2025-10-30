# models/payment.py
from extensions import db
from datetime import datetime

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    amount = db.Column(db.Float)
    teacher_share = db.Column(db.Float)
    admin_share = db.Column(db.Float)
    status = db.Column(db.String(50), default="Pending")
    transaction_id = db.Column(db.String(100), nullable=True)
    teacher_paid = db.Column(db.Boolean, default=False)
    admin_paid = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    student = db.relationship('User', foreign_keys=[student_id], back_populates='payments')
    teacher = db.relationship('User', foreign_keys=[teacher_id])
    course = db.relationship('Course', back_populates='payments')
