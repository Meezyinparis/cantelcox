from db import get_sqlalchemy_session
from models.order import Order
from models.order_item import OrderItem


def get_order_by_id(order_id):

    session = get_sqlalchemy_session()

    try:

        order = session.query(Order).filter_by(id=order_id).first()

        if not order:
            return {}

        items = session.query(OrderItem).filter_by(
            order_id=order_id
        ).all()

        return {

            "id": order.id,
            "customer_id": order.customer_id,
            "line_id": order.line_id,
            "order_status": order.order_status,
            "idempotency_key": order.idempotency_key,

            "items": [

                {

                    "plan_id": item.plan_id,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price)

                }

                for item in items

            ]

        }

    finally:
        session.close()
