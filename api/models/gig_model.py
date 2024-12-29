#deprecated Not used

import os
import sqlite3

DB_PATH = os.getenv("DB_PATH", "database.db")

def init_gig_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS connected_platforms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            access_token TEXT NOT NULL,
            refresh_token TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from api.config.database import Base
from api.utils.encryption_utils import EncryptionManager
import enum

# Initialize encryption manager
encryption_manager = EncryptionManager()

class PlatformType(str, enum.Enum):
    UBER = "uber"
    LYFT = "lyft"
    DOORDASH = "doordash"
    INSTACART = "instacart"

class GigPlatformStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ERROR = "error"

class TripStatus(str, enum.Enum):
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"

class GigPlatform(Base):
    __tablename__ = "gig_platforms"
    __table_args__ = (
        Index('idx_gig_platform_user', 'user_id'),
        Index('idx_gig_platform_status', 'account_status'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    platform = Column(Enum(PlatformType), nullable=False)
    platform_user_id = Column(String(255))
    platform_email = Column(String(255))
    
    # Encrypted fields
    access_token = Column(String(1024))
    refresh_token = Column(String(1024))
    
    # Platform details
    account_status = Column(Enum(GigPlatformStatus), default=GigPlatformStatus.PENDING)
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime(timezone=True))
    error_message = Column(String)
    
    # Metadata and audit
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships with cascade delete
    user = relationship("Users", back_populates="gig_platforms")
    earnings = relationship("GigEarnings", back_populates="platform", cascade="all, delete-orphan")
    trips = relationship("GigTrip", back_populates="platform", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        if 'access_token' in kwargs:
            kwargs['access_token'] = encryption_manager.encrypt(kwargs['access_token'])
        if 'refresh_token' in kwargs:
            kwargs['refresh_token'] = encryption_manager.encrypt(kwargs['refresh_token'])
        super().__init__(**kwargs)

    @property
    def decrypted_access_token(self):
        return encryption_manager.decrypt(self.access_token) if self.access_token else None

    @property
    def decrypted_refresh_token(self):
        return encryption_manager.decrypt(self.refresh_token) if self.refresh_token else None

class GigTrip(Base):
    __tablename__ = "gig_trips"
    __table_args__ = (
        Index('idx_gig_trip_platform', 'platform_id'),
        Index('idx_gig_trip_status', 'status'),
    )

    id = Column(Integer, primary_key=True, index=True)
    platform_id = Column(Integer, ForeignKey("gig_platforms.id", ondelete="CASCADE"))
    trip_id = Column(String, unique=True)
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    
    # Financial details
    base_fare = Column(Float)
    tips = Column(Float)
    bonuses = Column(Float)
    platform_fees = Column(Float)
    
    # Trip details
    distance = Column(Float)
    duration = Column(Integer)  # in seconds
    status = Column(Enum(TripStatus), default=TripStatus.PENDING)
    
    # Additional data
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    platform = relationship("GigPlatform", back_populates="trips")
    income = relationship("Income", back_populates="trip", cascade="all, delete-orphan")
    expenses = relationship("Expenses", back_populates="trip", cascade="all, delete-orphan")

    @property
    def total_earnings(self):
        return sum(filter(None, [self.base_fare, self.tips, self.bonuses]))

class GigEarnings(Base):
    __tablename__ = "gig_earnings"
    __table_args__ = (
        Index('idx_gig_earnings_platform', 'platform_id'),
        Index('idx_gig_earnings_period', 'period_start', 'period_end'),
    )

    id = Column(Integer, primary_key=True, index=True)
    platform_id = Column(Integer, ForeignKey("gig_platforms.id", ondelete="CASCADE"))
    period_start = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))
    
    # Earnings breakdown
    gross_earnings = Column(Float)
    net_earnings = Column(Float)
    platform_fees = Column(Float)
    tips = Column(Float)
    bonuses = Column(Float)
    
    # Statistics
    trips_count = Column(Integer)
    total_distance = Column(Float)
    total_duration = Column(Integer)  # in seconds
    
    # Additional data
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    platform = relationship("GigPlatform", back_populates="earnings")
