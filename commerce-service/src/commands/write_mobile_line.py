from datetime import datetime
from logger import Logger
from models.mobile_line import MobileLine
from db import get_sqlalchemy_session

logger = Logger.get_instance("write_mobile_line")


def activate_mobile_line(customer_id: int, msisdn: str, sim_number: str):
    """Activate mobile line in MySQL"""

    if not customer_id or not msisdn or not sim_number:
        raise ValueError("Cannot activate line. Missing required information.")

    session = get_sqlalchemy_session()

    try:
        logger.debug("Commencer : activation de ligne")

        new_line = MobileLine(
            customer_id=customer_id,
            msisdn=msisdn,
            sim_number=sim_number,
            line_status="ACTIVE",
            activated_at=datetime.now()
        )

        session.add(new_line)
        session.flush()
        session.commit()

        logger.debug("Une ligne mobile a été activée")
        return new_line.id

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()


def delete_mobile_line(line_id: int):
    """Delete mobile line in MySQL"""

    session = get_sqlalchemy_session()

    try:
        line = session.query(MobileLine).filter(
            MobileLine.id == line_id).first()

        if line:
            session.delete(line)
            session.commit()
            return 1

        return 0

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()
