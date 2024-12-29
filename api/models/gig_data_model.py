from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from api.config.database import Base

class PlatformType(enum.Enum):
    UBER = "uber"
    LYFT = "lyft"
    DOORDASH = "doordash"
    INSTACART = "instacart"

class GigPlatform(Base):
    __tablename__ = "gig_platforms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    platform = Column(Enum(PlatformType))
    access_token = Column(String)
    refresh_token = Column(String)
    last_sync = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("Users", back_populates="gig_platforms")
    trips = relationship("GigTrip", back_populates="platform")

class GigTrip(Base):
    __tablename__ = "gig_trips"

    id = Column(Integer, primary_key=True, index=True)
    platform_id = Column(Integer, ForeignKey("gig_platforms.id", ondelete="CASCADE"))
    trip_id = Column(String, unique=True)
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    earnings = Column(Float)
    distance = Column(Float)
    status = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    platform = relationship("GigPlatform", back_populates="trips")
    income = relationship("Income", back_populates="trip")
    expenses = relationship("Expenses", back_populates="trip")
