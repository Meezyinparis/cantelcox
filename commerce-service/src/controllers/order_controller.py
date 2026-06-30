import requests
from flask import jsonify

from commands.write_order import add_order, delete_order
from queries.read_order import get_order_by_id


def create_order(request):
    """Create order"""

    payload = request.get_json() or {}

    customer_id = payload.get("customer_id")
    line_id = payload.get("line_id")
    idempotency_key = payload.get("idempotency_key")
    items = payload.get("items")

    if not customer_id or not line_id or not idempotency_key or not items:
        return jsonify({
            "error": "customer_id, line_id, idempotency_key and items are required"
        }), 400

    try:
        customer_response = requests.get(
            f"http://krakend:8080/v1/customers/{customer_id}",
            timeout=5
        )

        if customer_response.status_code == 404:
            return jsonify({
                "error": "Customer not found"
            }), 404

        if customer_response.status_code != 200:
            return jsonify({
                "error": "Could not validate customer"
            }), 502

        customer = customer_response.json()

        if customer.get("status") != "ACTIVE":
            return jsonify({
                "error": "Customer account is not active"
            }), 403

        order_id = add_order(
            customer_id,
            line_id,
            idempotency_key,
            items
        )

        return jsonify({
            "order_id": order_id
        }), 201

    except requests.exceptions.RequestException:
        return jsonify({
            "error": "Identity service unavailable"
        }), 503

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
