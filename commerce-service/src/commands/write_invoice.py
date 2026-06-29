from logger import Logger
from db import get_sqlalchemy_session, get_redis_conn
from models.invoice import Invoice

logger = Logger.get_instance("write_invoice")


def add_invoice(customer_id: int,
                line_id: int,
                billing_cycle: str,
                amount: float):
    """Insert invoice in MySQL and Redis"""

    session = get_sqlalchemy_session()

    try:
        logger.debug("Commencer : création facture")

        invoice = Invoice(
            customer_id=customer_id,
            line_id=line_id,
            billing_cycle=billing_cycle,
            amount=amount,
            invoice_status="UNPAID"
        )

        session.add(invoice)
        session.flush()
        session.commit()

        add_invoice_to_redis(invoice)

        logger.debug("Facture créée")

        return invoice.id

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()


def delete_invoice(invoice_id: int):
    """Delete invoice in MySQL and Redis"""

    session = get_sqlalchemy_session()

    try:
        invoice = session.query(Invoice).filter(
            Invoice.id == invoice_id
        ).first()

        if invoice:
            session.delete(invoice)
            session.commit()

            delete_invoice_from_redis(invoice_id)

            return 1

        return 0

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()


def add_invoice_to_redis(invoice):
    """Insert invoice to Redis"""

    r = get_redis_conn()

    r.hset(
        f"invoice:{invoice.id}",
        mapping={
            "id": invoice.id,
            "customer_id": invoice.customer_id,
            "line_id": invoice.line_id,
            "billing_cycle": invoice.billing_cycle,
            "amount": float(invoice.amount),
            "invoice_status": invoice.invoice_status
        }
    )


def delete_invoice_from_redis(invoice_id):
    """Delete invoice from Redis"""

    r = get_redis_conn()
    r.delete(f"invoice:{invoice_id}")