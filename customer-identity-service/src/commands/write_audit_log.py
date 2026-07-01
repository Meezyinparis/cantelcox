from models.audit_log import AuditLog
from db import get_sqlalchemy_session


def add_audit_log(
    event_type: str,
    entity_type: str,
    entity_id=None,
    actor_id=None,
    trace_id=None,
    payload=None
):
    session = get_sqlalchemy_session()

    try:
        audit = AuditLog(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=actor_id,
            trace_id=trace_id,
            payload=payload
        )

        session.add(audit)
        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
