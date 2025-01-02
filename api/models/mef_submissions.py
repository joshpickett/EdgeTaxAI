from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from api.config.database import Base


class SubmissionStatus(enum.Enum):
    PENDING = "pending"
    TRANSMITTED = "transmitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    ERROR = "error"
    FAILED = "failed"


class MeFSubmission(Base):
    __tablename__ = "mef_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    submission_id = Column(String(100), unique=True)
    form_type = Column(String(50))
    status = Column(SQLEnum(SubmissionStatus), default=SubmissionStatus.PENDING)
    transmission_attempts = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)
    submitted_at = Column(DateTime(timezone=True))
    acknowledgment_timestamp = Column(DateTime(timezone=True))
    audit_trail = Column(JSONB, default={})
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    processing_history = Column(JSONB, default=[])
    validation_results = Column(JSONB, default={})
    security_checks = Column(JSONB, default={})
    error_details = Column(JSONB, default={})
    error_message = Column(String(500))
    xml_content = Column(String)  # Stored XML payload
    acknowledgment_data = Column(String)  # Stored acknowledgment XML

    # Relationships
    user = relationship("Users", back_populates="mef_submissions")
