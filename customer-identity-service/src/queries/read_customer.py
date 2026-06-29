from db import get_sqlalchemy_session
from models.customer import Customer


def get_customer_by_id(customer_id):
    """Get customer by ID"""

    session = get_sqlalchemy_session()

    result = session.query(Customer).filter_by(id=customer_id).all()

    if len(result):

        customer = result[0]

        return {
            "id": customer.id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "email": customer.email,
            "phone_number": customer.phone_number
        }

    return {}