from flask import jsonify

from commands.write_usage import add_usage
from queries.read_usage import get_usage_by_line_id


def create_usage(request):

    payload = request.get_json() or {}

    try:

        usage_id = add_usage(

            payload.get("line_id"),
            payload.get("voice_minutes_used"),
            payload.get("sms_used"),
            payload.get("data_used_gb"),
            payload.get("usage_period")

        )

        return jsonify({

            "usage_id": usage_id

        }), 201

    except Exception as e:

        return jsonify({

            "error": str(e)

        }), 500


def get_usage(line_id):

    try:

        usage = get_usage_by_line_id(line_id)

        if usage:

            return jsonify(usage), 200

        return jsonify({

            "error": "Usage not found"

        }), 404

    except Exception as e:

        return jsonify({

            "error": str(e)

        }), 500
