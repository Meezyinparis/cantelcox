import bcrypt
import random
from datetime import datetime, timedelta

import jwt
from flask import jsonify

from config import JWT_SECRET, JWT_ALGORITHM
from commands.write_mfa_otp import add_mfa_otp, mark_otp_as_used
from queries.read_mfa_otp import get_valid_otp
from queries.read_user_account import get_user_account_by_email
from commands.write_audit_log import add_audit_log


def request_mfa(request):
    """Generate MFA OTP"""

    payload = request.get_json() or {}

    email = payload.get("email")
    password = payload.get("password")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    if not password:
        return jsonify({"error": "Password is required"}), 400

    user_account = get_user_account_by_email(email)

    if not user_account:
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    if not bcrypt.checkpw(
        password.encode("utf-8"),
        user_account["password_hash"].encode("utf-8")
    ):
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    otp_code = str(random.randint(100000, 999999))

    add_mfa_otp(
        user_account["id"],
        otp_code,
        "LOGIN"
    )

    add_audit_log(
        event_type="MFA_REQUESTED",
        entity_type="UserAccount",
        entity_id=user_account["id"],
        actor_id=user_account["customer_id"],
        payload={
            "email": email
        }
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

    add_audit_log(
        event_type="MFA_VERIFIED",
        entity_type="UserAccount",
        entity_id=user_account["id"],
        actor_id=user_account["customer_id"],
        payload={
            "email": email
        }
    )

    return jsonify({
        "message": "MFA verified",
        "token": token
    }), 200


def validate_jwt(request):
    """Validate JWT token"""

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return jsonify({
            "error": "Missing JWT token"
        }), 401

    if not auth_header.startswith("Bearer "):
        return jsonify({
            "error": "Invalid authorization format"
        }), 401

    token = auth_header.split(" ", 1)[1]

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        add_audit_log(
            event_type="JWT_VALIDATED",
            entity_type="UserAccount",
            entity_id=payload["user_account_id"],
            actor_id=payload["customer_id"]
        )

        return jsonify({
            "valid": True,
            "customer_id": payload["customer_id"],
            "user_account_id": payload["user_account_id"],
            "email": payload["email"]
        }), 200

    except jwt.ExpiredSignatureError:
        add_audit_log(
            event_type="JWT_EXPIRED",
            entity_type="UserAccount"
        )

        return jsonify({
            "error": "JWT has expired"
        }), 401

    except jwt.InvalidTokenError:
        add_audit_log(
            event_type="JWT_INVALID",
            entity_type="UserAccount"
        )

        return jsonify({
            "error": "Invalid JWT"
        }), 401
