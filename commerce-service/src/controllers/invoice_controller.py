from flask import jsonify

from commands.write_invoice import add_invoice, delete_invoice
from queries.read_invoice import (
    get_invoice_by_id,
    get_invoices_by_line_id
)


def create_invoice(request):
    """Create invoice"""

    payload = request.get_json() or {}

    try:
        invoice_id = add_invoice(
            payload.get("customer_id"),
            payload.get("line_id"),
            payload.get("billing_cycle"),
            payload.get("amount")
        )

        return jsonify({
            "invoice_id": invoice_id
        }), 201

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


def remove_invoice(invoice_id):
    """Delete invoice"""

    try:
        deleted = delete_invoice(invoice_id)

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


def get_invoice(invoice_id):
    """Get invoice by ID"""

    try:
        invoice = get_invoice_by_id(invoice_id)

        if invoice:
            return jsonify(invoice), 200

        return jsonify({
            "error": "Invoice not found"
        }), 404

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


def get_line_invoices(line_id):
    """Get invoices for one mobile line"""

    try:
        invoices = get_invoices_by_line_id(line_id)
        return jsonify(invoices), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500