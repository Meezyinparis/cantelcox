from db import get_sqlalchemy_session, get_redis_conn
from models.usage_record import UsageRecord


def add_usage(line_id,
              voice_minutes,
              sms_used,
              data_used_gb,
              usage_period):

    session = get_sqlalchemy_session()

    try:

        usage = UsageRecord(
            line_id=line_id,
            voice_minutes_used=voice_minutes,
            sms_used=sms_used,
            data_used_gb=data_used_gb,
            usage_period=usage_period
        )

        session.add(usage)
        session.flush()
        session.commit()

        add_usage_to_redis(usage)

        return usage.id

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()


def add_usage_to_redis(usage):

    r = get_redis_conn()

    r.hset(

        f"usage:{usage.line_id}",

        mapping={

            "id": usage.id,
            "line_id": usage.line_id,
            "voice_minutes_used": usage.voice_minutes_used,
            "sms_used": usage.sms_used,
            "data_used_gb": float(usage.data_used_gb),
            "usage_period": usage.usage_period

        }

    )


def delete_usage_from_redis(line_id):

    r = get_redis_conn()

    r.delete(f"usage:{line_id}")