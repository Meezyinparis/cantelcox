from flask import jsonify

from commands.write_user_account import (
    add_user_account,
    delete_user_account
)

from queries.read_user_account import (
    get_user_account_by_id
)


def create_user_account(request):
    """Create user account"""

    payload = request.get_json() or {}

    customer_id = payload.get("customer_id")
    email = payload.get("email")
    password_hash = payload.get("password_hash")

    try:
        account_id = add_user_account(
            customer_id,
            email,
            password_hash
        )

        return jsonify({
            "user_account_id": account_id
        }), 201

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


def remove_user_account(account_id):
    """Delete user account"""

    try:
        deleted = delete_user_account(account_id)

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


def get_user_account(account_id):
    """Get user account"""
    try:
        account = get_user_account_by_id(account_id)
        return jsonify(account), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500