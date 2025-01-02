from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    Enum as SQLAlchemyEnum,
)
from sqlalchemy.orm import relationship
import enum
from api.config.database import Base
from sqlalchemy.sql import func


class DeductionType(enum.Enum):
    MILEAGE = "mileage"
    HOME_OFFICE = "home_office"
    SUPPLIES = "supplies"
    EQUIPMENT = "equipment"
    OTHER = "other"


class Deductions(Base):
    __tablename__ = "deductions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    type = Column(SQLAlchemyEnum(DeductionType))
    description = Column(String(500))
    amount = Column(Numeric(10, 2))
    calculated_amount = Column(Numeric(10, 2))
    tax_year = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user = relationship("Users", back_populates="deductions")
