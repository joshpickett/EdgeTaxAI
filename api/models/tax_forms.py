from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum as SQLAlchemyEnum,
)
from sqlalchemy.orm import relationship
import enum
from api.config.database import Base
from sqlalchemy.sql import func


class FormStatus(enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class FormType(enum.Enum):
    W2 = "w2"
    TEN_NINETY_NINE = "1099"
    SCHEDULE_C = "schedule_c"
    OTHER = "other"


class TaxForms(Base):
    __tablename__ = "tax_forms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    form_type = Column(SQLAlchemyEnum(FormType))
    tax_year = Column(Integer)
    status = Column(SQLAlchemyEnum(FormStatus), default=FormStatus.DRAFT)
    form_data = Column(String)  # JSON string
    submitted_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user = relationship("Users", back_populates="tax_forms")
