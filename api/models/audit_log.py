from sqlalchemy import Column, Integer, String, DateTime, JSON
from api.config.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=True)
    event_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    device_fingerprint = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=False)
