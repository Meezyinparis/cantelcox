import random
from datetime import datetime, timedelta

import jwt
from flask import jsonify

from config import JWT_SECRET, JWT_ALGORITHM
from commands.write_mfa_otp import add_mfa_otp, mark_otp_as_used
from queries.read_mfa_otp import get_valid_otp
from queries.read_user_account import get_user_account_by_email


def request_mfa(request):
    """Generate MFA OTP"""

    payload = request.get_json() or {}
    email = payload.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user_account = get_user_account_by_email(email)

    if not user_account:
        return jsonify({"error": "User account not found"}), 404

    otp_code = str(random.randint(100000, 999999))

    add_mfa_otp(
        user_account["id"],
        otp_code,
        "LOGIN"
    )

    return jsonify({
        "message": "OTP generated",
        "otp": otp_code
    }), 200


def verify_mfa(request):
    """Verify MFA OTP and return JWT"""

    payload = request.get_json() or {}
    email = payload.get("email")
    otp_code = payload.get("otp")

    if not email or not otp_code:
        return jsonify({"error": "Email and OTP are required"}), 400

    user_account = get_user_account_by_email(email)

    if not user_account:
        return jsonify({"error": "User account not found"}), 404

    otp = get_valid_otp(
        user_account["id"],
        otp_code
    )

    if not otp:
        return jsonify({"error": "Invalid or expired OTP"}), 401

    mark_otp_as_used(otp["id"])

    token_payload = {
        "user_account_id": user_account["id"],
        "customer_id": user_account["customer_id"],
        "email": user_account["email"],
        "exp": datetime.utcnow() + timedelta(hours=1)
    }

    token = jwt.encode(
        token_payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )

    return jsonify({
        "message": "MFA verified",
        "token": token
    }), 200
