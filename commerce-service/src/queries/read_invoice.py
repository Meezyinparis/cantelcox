from db import get_sqlalchemy_session, get_redis_conn
from models.invoice import Invoice


def get_invoice_by_id_redis(invoice_id):
    """Get invoice by ID from Redis"""

    r = get_redis_conn()
    raw_invoice = r.hgetall(f"invoice:{invoice_id}")

    invoice = {}

    for key, value in raw_invoice.items():
        found_key = key.decode("utf-8") if isinstance(key, bytes) else key
        found_value = value.decode(
            "utf-8") if isinstance(value, bytes) else value
        invoice[found_key] = found_value

    return invoice


def get_invoice_by_id_mysql(invoice_id):
    """Get invoice by ID from MySQL"""

    session = get_sqlalchemy_session()

    try:
        result = session.query(Invoice).filter_by(
            id=invoice_id
        ).all()

        if len(result):
            invoice = result[0]

            return {
                "id": invoice.id,
                "customer_id": invoice.customer_id,
                "line_id": invoice.line_id,
                "billing_cycle": invoice.billing_cycle,
                "amount": round(float(invoice.amount), 2),
                "invoice_status": invoice.invoice_status
            }

        return {}

    finally:
        session.close()


def get_invoices_by_line_id_redis(line_id):
    """Get invoices by line ID from Redis"""

    result = []

    try:
        r = get_redis_conn()
        invoice_keys = r.keys("invoice:*")

        for key in invoice_keys:
            raw_invoice = r.hgetall(key)

            invoice = {}
            for field, value in raw_invoice.items():
                found_key = field.decode(
                    "utf-8") if isinstance(field, bytes) else field
                found_value = value.decode(
                    "utf-8") if isinstance(value, bytes) else value
                invoice[found_key] = found_value

            if invoice and str(invoice.get("line_id")) == str(line_id):
                result.append({
                    "id": int(invoice["id"]),
                    "customer_id": int(invoice["customer_id"]),
                    "line_id": int(invoice["line_id"]),
                    "billing_cycle": invoice["billing_cycle"],
                    "amount": round(float(invoice["amount"]), 2),
                    "invoice_status": invoice["invoice_status"]
                })

    except Exception as e:
        return {"error": str(e)}

    return result


def get_invoices_by_line_id_mysql(line_id):
    """Get all invoices for one mobile line from MySQL"""

    session = get_sqlalchemy_session()
    result = []

    try:
        invoices = session.query(Invoice).filter_by(
            line_id=line_id
        ).all()

        for invoice in invoices:
            result.append({
                "id": invoice.id,
                "customer_id": invoice.customer_id,
                "line_id": invoice.line_id,
                "billing_cycle": invoice.billing_cycle,
                "amount": round(float(invoice.amount), 2),
                "invoice_status": invoice.invoice_status
            })

        return result

    finally:
        session.close()


def get_invoice_by_id(invoice_id):
    """Get invoice by ID"""

    invoice = get_invoice_by_id_redis(invoice_id)

    if invoice:
        return invoice

    return get_invoice_by_id_mysql(invoice_id)


def get_invoices_by_line_id(line_id):
    """Get invoices by line ID"""

    invoices = get_invoices_by_line_id_redis(line_id)

    if invoices:
        return invoices

    return get_invoices_by_line_id_mysql(line_id)
