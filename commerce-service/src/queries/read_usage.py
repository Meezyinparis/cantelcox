from db import get_redis_conn, get_sqlalchemy_session
from models.usage_record import UsageRecord


def get_usage_by_line_id_redis(line_id):

    r = get_redis_conn()

    raw_usage = r.hgetall(f"usage:{line_id}")

    usage = {}

    for key, value in raw_usage.items():

        found_key = key.decode("utf-8") if isinstance(key, bytes) else key
        found_value = value.decode("utf-8") if isinstance(value, bytes) else value

        usage[found_key] = found_value

    return usage


def get_usage_by_line_id_mysql(line_id):

    session = get_sqlalchemy_session()

    try:

        result = session.query(UsageRecord).filter_by(
            line_id=line_id
        ).all()

        if len(result):

            usage = result[0]

            return {

                "id": usage.id,
                "line_id": usage.line_id,
                "voice_minutes_used": usage.voice_minutes_used,
                "sms_used": usage.sms_used,
                "data_used_gb": round(float(usage.data_used_gb),2),
                "usage_period": usage.usage_period

            }

        return {}

    finally:

        session.close()


def get_usage_by_line_id(line_id):

    usage = get_usage_by_line_id_redis(line_id)

    if usage:

        return usage

    return get_usage_by_line_id_mysql(line_id)