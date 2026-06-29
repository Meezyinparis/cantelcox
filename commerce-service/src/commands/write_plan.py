from logger import Logger
from models.plan import Plan
from db import get_sqlalchemy_session, get_redis_conn

logger = Logger.get_instance("write_plan")


def add_plan(name: str, description: str, monthly_price: float,
             data_limit_gb: int, voice_minutes: int, sms_limit: int):
    """Insert plan in MySQL, keep Redis in sync"""

    if not name or monthly_price is None:
        raise ValueError("Cannot create plan. A plan must have name and monthly_price.")

    session = get_sqlalchemy_session()

    try:
        logger.debug("Commencer : ajout de forfait")

        new_plan = Plan(
            name=name,
            description=description,
            monthly_price=monthly_price,
            data_limit_gb=data_limit_gb,
            voice_minutes=voice_minutes,
            sms_limit=sms_limit,
            active=True
        )

        session.add(new_plan)
        session.flush()
        session.commit()

        add_plan_to_redis(new_plan)

        logger.debug("Un forfait a été ajouté")
        return new_plan.id

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()


def delete_plan(plan_id: int):
    """Soft delete plan in MySQL, keep Redis in sync"""

    session = get_sqlalchemy_session()

    try:
        plan = session.query(Plan).filter(Plan.id == plan_id).first()

        if plan:
            plan.active = False
            session.commit()

            delete_plan_from_redis(plan_id)
            delete_active_plans_cache()

            return 1

        return 0

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()


def add_plan_to_redis(plan):
    """Insert plan to Redis"""

    r = get_redis_conn()

    plan_data = {
        "id": plan.id,
        "name": plan.name,
        "description": plan.description,
        "monthly_price": float(plan.monthly_price),
        "data_limit_gb": plan.data_limit_gb,
        "voice_minutes": plan.voice_minutes,
        "sms_limit": plan.sms_limit,
        "active": plan.active
    }

    r.hset(
        f"plan:{plan.id}",
        mapping={
            "id": plan.id,
            "name": plan.name,
            "description": plan.description or "",
            "monthly_price": float(plan.monthly_price),
            "data_limit_gb": plan.data_limit_gb or 0,
            "voice_minutes": plan.voice_minutes or 0,
            "sms_limit": plan.sms_limit or 0,
            "active": int(plan.active)
        }
    )

    r.delete("plans:active")


def delete_plan_from_redis(plan_id):
    """Delete plan from Redis"""

    r = get_redis_conn()
    r.delete(f"plan:{plan_id}")


def delete_active_plans_cache():
    """Delete active plans list from Redis"""

    r = get_redis_conn()
    r.delete("plans:active")