import requests
from flask import jsonify

from commands.write_mobile_line import activate_mobile_line, delete_mobile_line
from queries.read_mobile_line import (
    get_mobile_line_by_id,
    get_mobile_lines_by_customer_id
)


def activate_line(request):
    """Activate mobile line"""

    payload = request.get_json() or {}

    customer_id = payload.get("customer_id")
    msisdn = payload.get("msisdn")
    sim_number = payload.get("sim_number")

    try:
        line_id = activate_mobile_line(
            customer_id,
            msisdn,
            sim_number
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
