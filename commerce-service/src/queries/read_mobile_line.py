from db import get_sqlalchemy_session
from models.mobile_line import MobileLine


def get_mobile_line_by_id(line_id):
    """Get mobile line by ID"""

    session = get_sqlalchemy_session()

    try:
        result = session.query(MobileLine).filter_by(id=line_id).all()

        if len(result):
            line = result[0]

            return {
                "id": line.id,
                "customer_id": line.customer_id,
                "msisdn": line.msisdn,
                "sim_number": line.sim_number,
                "line_status": line.line_status,
                "activated_at": str(line.activated_at)
            }

        return {}

    finally:
        session.close()


def get_mobile_lines_by_customer_id(customer_id):
    """Get mobile lines by customer ID"""

    session = get_sqlalchemy_session()
    result = []

    try:
        lines = session.query(MobileLine).filter_by(
            customer_id=customer_id).all()

        for line in lines:
            result.append({
                "id": line.id,
                "customer_id": line.customer_id,
                "msisdn": line.msisdn,
                "sim_number": line.sim_number,
                "line_status": line.line_status,
                "activated_at": str(line.activated_at)
            })

        return result

    finally:
        session.close()
