# utils/decorators.py
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models import User

def role_required(role):
    """Restrict access to users with a specific role (e.g., 'student', 'teacher', 'admin')."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Ensure JWT is present and valid
            try:
                verify_jwt_in_request()
            except Exception:
                return jsonify({'message': 'Missing or invalid token'}), 401

            user_identity = get_jwt_identity()

            # Handle both email-based or id-based JWT identities
            user = None
            if isinstance(user_identity, dict) and 'id' in user_identity:
                user = User.query.get(user_identity['id'])
            else:
                user = User.query.filter_by(email=user_identity).first()

            if not user:
                return jsonify({'message': 'User not found'}), 404

            if user.role != role:
                return jsonify({'message': f'Access denied. Requires {role} role.'}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator
