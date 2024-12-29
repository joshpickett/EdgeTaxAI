from sqlalchemy import Column, Numeric, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from api.config.database import Base

class Expenses(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    description = Column(String(500))
    amount = Column(Numeric(10, 2))
    date = Column(DateTime(timezone=True))
    trip_id = Column(Integer, ForeignKey("gig_trips.id"))
    trip = relationship("GigTrip", back_populates="expenses")
