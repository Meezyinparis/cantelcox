import requests
from flask import jsonify

from commands.write_order import add_order, delete_order
from queries.read_order import get_order_by_id
from commands.write_audit_log import add_audit_log


def create_order(request):
    """Create order"""

    payload = request.get_json() or {}

    customer_id = payload.get("customer_id")
    line_id = payload.get("line_id")
    idempotency_key = payload.get("idempotency_key")
    items = payload.get("items")

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return jsonify({"error": "Missing JWT token"}), 401

    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Invalid authorization format"}), 401

    auth_response = requests.post(
        "http://krakend:8080/v1/auth/validate",
        headers={"Authorization": auth_header},
        timeout=3
    )

    if auth_response.status_code != 200:
        return jsonify({"error": "Invalid JWT"}), 401

    if not customer_id or not line_id or not idempotency_key or not items:
        return jsonify({
            "error": "customer_id, line_id, idempotency_key and items are required"
        }), 400

    try:
        customer_response = requests.get(
            f"http://krakend:8080/v1/customers/{customer_id}",
            timeout=3
        )

        if customer_response.status_code == 404:
            add_audit_log(
                event_type="ORDER_CREATION_FAILED",
                entity_type="Order",
                actor_id=customer_id,
                payload={
                    "line_id": line_id,
                    "error": "Customer not found"
                }
            )
            return jsonify({
                "error": "Customer not found"
            }), 404

        if customer_response.status_code != 200:
            add_audit_log(
                event_type="ORDER_CREATION_FAILED",
                entity_type="Order",
                actor_id=customer_id,
                payload={
                    "line_id": line_id,
                    "error": "Could not validate customer"
                }
            )
            return jsonify({
                "error": "Could not validate customer"
            }), 502

        customer = customer_response.json()

        if customer.get("status") != "ACTIVE":
            add_audit_log(
                event_type="ORDER_CREATION_FAILED",
                entity_type="Order",
                actor_id=customer_id,
                payload={
                    "line_id": line_id,
                    "error": "Customer account is not active"
                }
            )
            return jsonify({
                "error": "Customer account is not active"
            }), 403

        order_id = add_order(
            customer_id,
            line_id,
            idempotency_key,
            items
        )

        add_audit_log(
            event_type="ORDER_CREATED",
            entity_type="Order",
            entity_id=order_id,
            actor_id=customer_id,
            payload={
                "line_id": line_id
            }
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
