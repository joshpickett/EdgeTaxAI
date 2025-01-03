from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from api.config.database import Base

class Income(Base):
    __tablename__ = "income"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    amount = Column(Numeric(10, 2))
    platform_fees = Column(Numeric(10, 2), default=0.00)
    mileage = Column(Numeric(10, 2), default=0.00)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    description = Column(String(500))

    # Relationships
    user = relationship("Users", back_populates="income")

# Ensure the Users model exists and has a back_populates="income" relationship defined