from sqlalchemy import Column, Numeric, DateTime, Integer, ForeignKey, String, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from api.config.database import Base

class ExpenseCategory(enum.Enum):
    SUPPLIES = "supplies"
    EQUIPMENT = "equipment"
    VEHICLE = "vehicle"
    INSURANCE = "insurance"
    OFFICE = "office"
    OTHER = "other"

class Expenses(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    description = Column(String(500))
    amount = Column(Numeric(10, 2))
    date = Column(DateTime(timezone=True))
    category = Column(SQLEnum(ExpenseCategory))
    receipt_url = Column(String(512))
    transaction_id = Column(String(100))
    trip_id = Column(Integer, ForeignKey("gig_trips.id"))
    
    ...rest of the code...
