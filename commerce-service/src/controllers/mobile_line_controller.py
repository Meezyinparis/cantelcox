import requests
from flask import jsonify

from commands.write_mobile_line import activate_mobile_line, delete_mobile_line
from queries.read_mobile_line import (
    get_mobile_line_by_id,
    get_mobile_lines_by_customer_id
)
from commands.write_audit_log import add_audit_log


def activate_line(request):
    """Activate mobile line"""

    payload = request.get_json() or {}

    customer_id = payload.get("customer_id")
    msisdn = payload.get("msisdn")
    sim_number = payload.get("sim_number")
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return jsonify({"error": "Missing JWT token"}), 401

    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Invalid authorization format"}), 401

    if not customer_id or not msisdn or not sim_number:
        return jsonify({
            "error": "customer_id, msisdn and sim_number are required"
        }), 400

    response = requests.post(
        "http://krakend:8080/v1/auth/validate",
        headers={"Authorization": auth_header},
        timeout=3
    )

    if response.status_code != 200:
        add_audit_log(
            event_type="LINE_ACTIVATION_FAILED",
            entity_type="MobileLine",
            payload={
                "customer_id": customer_id,
                "msisdn": msisdn,
                "sim_number": sim_number,
                "error": "Invalid JWT"
            }
        )
        return jsonify({"error": "Invalid JWT"}), 401

    try:
        line_id = activate_mobile_line(
            customer_id,
            msisdn,
            sim_number
        )

        add_audit_log(
            event_type="LINE_ACTIVATED",
            entity_type="MobileLine",
            entity_id=line_id,
            actor_id=customer_id
        )

        return jsonify({"line_id": line_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def remove_line(line_id):
    """Delete mobile line"""

    try:
        deleted = delete_mobile_line(line_id)

        if deleted:
            return jsonify({"deleted": True}), 200

        return jsonify({"deleted": False}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_line(line_id):
    """Get mobile line"""

    try:
        line = get_mobile_line_by_id(line_id)

        if line:
            return jsonify(line), 200

        return jsonify({"error": "Line not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_customer_lines(customer_id):
    """Get all lines for a customer"""

    try:
        lines = get_mobile_lines_by_customer_id(customer_id)
        return jsonify(lines), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
