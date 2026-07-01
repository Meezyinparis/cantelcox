from sqlalchemy import Column, Integer, String, JSON, TIMESTAMP, text

from models.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    event_type = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(100))
    actor_id = Column(String(100))
    trace_id = Column(String(100))
    payload = Column(JSON)
    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )
