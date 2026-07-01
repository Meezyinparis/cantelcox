"""
Customer controller
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

from flask import jsonify

from commands.write_customer import add_customer, delete_customer
from commands.write_user_account import add_user_account
from queries.read_customer import get_customer_by_id
from commands.write_audit_log import add_audit_log


def create_customer(request):
    """Create customer and user account"""

    payload = request.get_json() or {}

    first_name = payload.get("first_name")
    last_name = payload.get("last_name")
    email = payload.get("email")
    phone_number = payload.get("phone_number")
    status = payload.get("status", "active")
    password = payload.get("password", "password_demo")

    try:
        customer_id = add_customer(
            first_name,
            last_name,
            email,
            phone_number,
            status
        )

        add_user_account(
            customer_id,
            email,
            password
        )

        add_audit_log(
            event_type="CUSTOMER_REGISTERED",
            entity_type="Customer",
            entity_id=customer_id,
            actor_id=customer_id,
            payload={
                "email": email
            }
        )

        return jsonify({
            "customer_id": customer_id
        }), 201

    except Exception as e:
        add_audit_log(
            event_type="CUSTOMER_REGISTRATION_FAILED",
            entity_type="Customer",
            payload={
                "email": email,
                "error": str(e)
            }
        )
        return jsonify({
            "error": str(e)
        }), 500


def remove_customer(customer_id):
    """Delete customer"""

    try:
        deleted = delete_customer(customer_id)

        if deleted:
            return jsonify({"deleted": True}), 200

        return jsonify({"deleted": False}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_customer(customer_id):
    """Get customer"""

    try:
        customer = get_customer_by_id(customer_id)

        if customer:
            return jsonify(customer), 200

        return jsonify({"error": "Customer not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
