from flask import jsonify

from commands.write_order import add_order, delete_order
from queries.read_order import get_order_by_id


def create_order(request):

    payload = request.get_json() or {}

    customer_id = payload.get("customer_id")
    line_id = payload.get("line_id")
    idempotency_key = payload.get("idempotency_key")
    items = payload.get("items")

    try:
        order_id = add_order(
            customer_id,
            line_id,
            idempotency_key,
            items
        )

        return jsonify({
            "order_id": order_id
        }), 201

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


def remove_order(order_id):

    try:
        deleted = delete_order(order_id)

        if deleted:
            return jsonify({
                "deleted": True
            }), 200

        return jsonify({
            "deleted": False
        }), 404

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


def get_order(order_id):
    try:
        order = get_order_by_id(order_id)

        if order:
            return jsonify(order), 200

        return jsonify({
            "error": "Order not found"
        }), 404

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
