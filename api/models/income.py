from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from api.config.database import Base

class Income(Base):
    __tablename__ = "income"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    platform_name = Column(String(50))
    gross_income = Column(Numeric(10, 2))
    tips = Column(Numeric(10, 2))
    platform_fees = Column(Numeric(10, 2))
    mileage = Column(Numeric(10, 2))
    payer_name = Column(String(100))
    tin = Column(String(11))
    total_compensation = Column(Numeric(10, 2))
    employer_name = Column(String(100))
    ein = Column(String(11))
    wages = Column(Numeric(10, 2))
    federal_withholding = Column(Numeric(10, 2))
    state_withholding = Column(Numeric(10, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    user = relationship("Users", back_populates="income")
