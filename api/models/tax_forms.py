from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum as SQLAlchemyEnum,
    JSON,
    Boolean,
)
from sqlalchemy.orm import relationship
import enum
from api.config.database import Base
from sqlalchemy.sql import func


class FormStatus(enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    AMENDED = "amended"


class FormType(enum.Enum):
    FORM_1040 = "1040"
    FORM_1040EZ = "1040ez"
    FORM_1099K = "1099-k"
    FORM_1099NEC = "1099-nec"
    SCHEDULE_A = "schedule_a"
    SCHEDULE_B = "schedule_b"
    SCHEDULE_C = "schedule_c"
    SCHEDULE_D = "schedule_d"
    SCHEDULE_E = "schedule_e"
    SCHEDULE_F = "schedule_f"
    FORM_2441 = "2441"
    FORM_2555 = "2555"
    FORM_3520 = "3520"
    FORM_4562 = "4562"
    FORM_4684 = "4684"
    FORM_5329 = "5329"
    FORM_5695 = "5695"
    FORM_8283 = "8283"
    FORM_8606 = "8606"
    FORM_8829 = "8829"
    FORM_8863 = "8863"
    FORM_8938 = "8938"
    FORM_8949 = "8949"
    FINCEN_114 = "fincen114"


class TaxForms(Base):
    __tablename__ = "tax_forms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    form_type = Column(SQLAlchemyEnum(FormType))
    tax_year = Column(Integer)
    status = Column(SQLAlchemyEnum(FormStatus), default=FormStatus.DRAFT)
    form_data = Column(JSON)  # Structured JSON data for the form
    
    # Validation and processing fields
    validation_errors = Column(JSON, nullable=True)
    processing_notes = Column(JSON, nullable=True)
    is_validated = Column(Boolean, default=False)
    
    # Filing tracking
    submitted_date = Column(DateTime(timezone=True))
    acceptance_date = Column(DateTime(timezone=True), nullable=True)
    rejection_date = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(String, nullable=True)
    
    # Amendment tracking
    is_amendment = Column(Boolean, default=False)
    original_form_id = Column(Integer, ForeignKey("tax_forms.id"), nullable=True)
    amendment_reason = Column(String, nullable=True)
    
    # Audit trail
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user = relationship("Users", back_populates="tax_forms")
    original_form = relationship("TaxForms", remote_side=[id])

    def __repr__(self):
        return f"<TaxForm(id={self.id}, type={self.form_type}, year={self.tax_year})>"