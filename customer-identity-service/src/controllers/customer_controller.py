from flask import jsonify

from commands.write_customer import (
    add_customer,
    delete_customer
)

from queries.read_customer import (
    get_customer_by_id
)


def create_customer(request):
    """Create customer"""

    payload = request.get_json() or {}

    first_name = payload.get("first_name")
    last_name = payload.get("last_name")
    email = payload.get("email")
    phone_number = payload.get("phone_number")

    try:

        customer_id = add_customer(
            first_name,
            last_name,
            email,
            phone_number
        )

        return jsonify({
            "customer_id": customer_id
        }), 201

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


def remove_customer(customer_id):
    """Delete customer"""

    try:

        deleted = delete_customer(customer_id)

        if deleted:
            return jsonify({
                "deleted": True
            })

        return jsonify({
            "deleted": False
        }), 404

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


def get_customer(customer_id):
    """Get customer"""

    try:

        customer = get_customer_by_id(customer_id)

        return jsonify(customer), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500
