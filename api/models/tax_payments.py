from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, String, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
import enum
from api.config.database import Base

class PaymentType(enum.Enum):
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    ESTIMATED = "estimated"
    ADJUSTMENT = "adjustment"

class TaxPayments(Base):
    __tablename__ = "tax_payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    amount = Column(Numeric(10, 2))
    payment_date = Column(DateTime(timezone=True))
    payment_type = Column(SQLAlchemyEnum(PaymentType))
    source = Column(String(100))
    confirmation_number = Column(String(100))
    
    ...rest of the code...
