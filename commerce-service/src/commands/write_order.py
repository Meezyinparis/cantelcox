from logger import Logger

from db import get_sqlalchemy_session
from models.order import Order
from models.order_item import OrderItem
from models.plan import Plan

logger = Logger.get_instance("write_order")


def add_order(customer_id: int,
              line_id: int,
              idempotency_key: str,
              items: list):
    """Insert order with items in MySQL"""

    if not items:
        raise ValueError(
            "Cannot create order. An order must contain at least one plan."
        )

    session = get_sqlalchemy_session()

    try:

        logger.debug("Commencer : ajout de commande")

        order = Order(
            customer_id=customer_id,
            line_id=line_id,
            order_status="CREATED",
            idempotency_key=idempotency_key
        )

        session.add(order)
        session.flush()

        for item in items:

            plan = session.query(Plan).filter(
                Plan.id == item["plan_id"],
                Plan.active == True
            ).first()

            if not plan:
                raise ValueError(
                    f"Plan {item['plan_id']} not found."
                )

            order_item = OrderItem(
                order_id=order.id,
                plan_id=plan.id,
                quantity=item["quantity"],
                unit_price=plan.monthly_price
            )

            session.add(order_item)

        session.commit()

        logger.debug("Commande créée")

        return order.id

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()


def delete_order(order_id: int):

    session = get_sqlalchemy_session()

    try:

        order = session.query(Order).filter(
            Order.id == order_id
        ).first()

        if order:

            session.delete(order)
            session.commit()

            return 1

        return 0

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()
