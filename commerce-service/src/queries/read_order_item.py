from db import get_sqlalchemy_session
from models.order_item import OrderItem


def get_order_items_by_order_id(order_id):
    """Get order items by order ID"""

    session = get_sqlalchemy_session()
    result = []

    try:
        items = session.query(OrderItem).filter_by(order_id=order_id).all()

        for item in items:
            result.append({
                "id": item.id,
                "order_id": item.order_id,
                "plan_id": item.plan_id,
                "quantity": item.quantity,
                "unit_price": round(float(item.unit_price), 2)
            })

        return result

    finally:
        session.close()