from db import get_redis_conn, get_sqlalchemy_session
from models.plan import Plan


def get_plan_by_id_redis(plan_id):
    """Get plan by ID from Redis"""
    r = get_redis_conn()
    raw_plan = r.hgetall(f"plan:{plan_id}")

    plan = {}
    for key, value in raw_plan.items():
        found_key = key.decode("utf-8") if isinstance(key, bytes) else key
        found_value = value.decode("utf-8") if isinstance(value, bytes) else value
        plan[found_key] = found_value

    return plan


def get_plan_by_id_mysql(plan_id):
    """Get plan by ID from MySQL"""
    session = get_sqlalchemy_session()

    try:
        result = session.query(Plan).filter_by(id=plan_id).all()

        if len(result):
            plan = result[0]
            return {
                "id": plan.id,
                "name": plan.name,
                "description": plan.description,
                "monthly_price": round(float(plan.monthly_price), 2),
                "data_limit_gb": plan.data_limit_gb,
                "voice_minutes": plan.voice_minutes,
                "sms_limit": plan.sms_limit,
                "active": plan.active
            }

        return {}

    finally:
        session.close()


def get_all_plans_mysql():
    """Get all active plans from MySQL"""
    session = get_sqlalchemy_session()
    result = []

    try:
        plans = session.query(Plan).filter_by(active=True).all()

        for plan in plans:
            result.append({
                "id": plan.id,
                "name": plan.name,
                "description": plan.description,
                "monthly_price": round(float(plan.monthly_price), 2),
                "data_limit_gb": plan.data_limit_gb,
                "voice_minutes": plan.voice_minutes,
                "sms_limit": plan.sms_limit,
                "active": plan.active
            })

        return result

    finally:
        session.close()


def get_all_plans_redis():
    """Get all plans from Redis"""
    result = []

    try:
        r = get_redis_conn()
        plan_keys = r.keys("plan:*")

        for key in plan_keys:
            raw_plan = r.hgetall(key)

            plan = {}
            for field, value in raw_plan.items():
                found_key = field.decode("utf-8") if isinstance(field, bytes) else field
                found_value = value.decode("utf-8") if isinstance(value, bytes) else value
                plan[found_key] = found_value

            if plan and plan.get("active") in ["1", "True", "true", True]:
                result.append({
                    "id": int(plan["id"]),
                    "name": plan["name"],
                    "description": plan.get("description"),
                    "monthly_price": round(float(plan["monthly_price"]), 2),
                    "data_limit_gb": int(plan.get("data_limit_gb", 0)),
                    "voice_minutes": int(plan.get("voice_minutes", 0)),
                    "sms_limit": int(plan.get("sms_limit", 0)),
                    "active": True
                })

    except Exception as e:
        return {"error": str(e)}

    return result


def get_plan_by_id(plan_id):
    """Get plan by ID from Redis"""
    plan = get_plan_by_id_redis(plan_id)

    if plan:
        return plan

    return get_plan_by_id_mysql(plan_id)


def get_all_plans():
    """Get all plans from Redis"""
    plans = get_all_plans_redis()

    if plans:
        return plans

    return get_all_plans_mysql()