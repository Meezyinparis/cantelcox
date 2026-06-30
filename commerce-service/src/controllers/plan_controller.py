from flask import jsonify

from commands.write_plan import add_plan, delete_plan
from queries.read_plan import get_all_plans, get_plan_by_id


def get_plans():
    """Get all active plans"""
    try:
        plans = get_all_plans()
        return jsonify(plans), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_plan(plan_id):
    """Get plan by ID"""
    try:
        plan = get_plan_by_id(plan_id)

        if plan:
            return jsonify(plan), 200

        return jsonify({"error": "Plan not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def activate_plan(request):
    """Create a new plan"""
    payload = request.get_json() or {}

    name = payload.get("name")
    description = payload.get("description")
    monthly_price = payload.get("monthly_price")
    data_limit_gb = payload.get("data_limit_gb")
    voice_minutes = payload.get("voice_minutes")
    sms_limit = payload.get("sms_limit")

    try:
        plan_id = add_plan(
            name,
            description,
            monthly_price,
            data_limit_gb,
            voice_minutes,
            sms_limit
        )

        return jsonify({"plan_id": plan_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def remove_plan(plan_id):
    """Delete a plan"""
    try:
        deleted = delete_plan(plan_id)

        if deleted:
            return jsonify({"deleted": True}), 200

        return jsonify({"deleted": False}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
