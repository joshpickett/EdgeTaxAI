from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum,
    Boolean,
    Index,
    JSON,
    Float
)
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
        Index("idx_gig_platform_user", "user_id"),
        Index("idx_gig_platform_status", "account_status"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform = Column(Enum(PlatformType), nullable=False)
    platform_user_id = Column(String(255), nullable=True)
    platform_email = Column(String(255), nullable=True)

    # Encrypted fields
    access_token = Column(String(1024), nullable=True)
    refresh_token = Column(String(1024), nullable=True)

    # Platform details
    account_status = Column(Enum(GigPlatformStatus), default=GigPlatformStatus.PENDING, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_sync = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(String, nullable=True)

    # Metadata and audit
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships with cascade delete
    user = relationship("Users", back_populates="gig_platforms")
    earnings = relationship(
        "GigEarnings", back_populates="platform", cascade="all, delete-orphan"
    )
    trips = relationship(
        "GigTrip", back_populates="platform", cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        if "access_token" in kwargs:
            kwargs["access_token"] = encryption_manager.encrypt(kwargs["access_token"])
        if "refresh_token" in kwargs:
            kwargs["refresh_token"] = encryption_manager.encrypt(
                kwargs["refresh_token"]
            )
        super().__init__(**kwargs)

    @property
    def decrypted_access_token(self):
        return (
            encryption_manager.decrypt(self.access_token) if self.access_token else None
        )

    @property
    def decrypted_refresh_token(self):
        return (
            encryption_manager.decrypt(self.refresh_token)
            if self.refresh_token
            else None
        )


class GigTrip(Base):
    __tablename__ = "gig_trips"
    __table_args__ = (
        Index("idx_gig_trip_platform", "platform_id"),
        Index("idx_gig_trip_status", "status"),
    )

    id = Column(Integer, primary_key=True, index=True)
    platform_id = Column(Integer, ForeignKey("gig_platforms.id", ondelete="CASCADE"), nullable=False)
    trip_id = Column(String, unique=True, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)

    # Financial details
    base_fare = Column(Float, nullable=True)
    tips = Column(Float, nullable=True)
    bonuses = Column(Float, nullable=True)
    platform_fees = Column(Float, nullable=True)

    # Trip details
    distance = Column(Float, nullable=True)
    duration = Column(Integer, nullable=True)  # in seconds
    status = Column(Enum(TripStatus), default=TripStatus.PENDING, nullable=False)

    # Additional data
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    platform = relationship("GigPlatform", back_populates="trips")
    income = relationship("Income", back_populates="trip", cascade="all, delete-orphan")
    expenses = relationship(
        "Expenses", back_populates="trip", cascade="all, delete-orphan"
    )

    @property
    def total_earnings(self):
        return sum(filter(None, [self.base_fare, self.tips, self.bonuses]))


class GigEarnings(Base):
    __tablename__ = "gig_earnings"
    __table_args__ = (
        Index("idx_gig_earnings_platform", "platform_id"),
        Index("idx_gig_earnings_period", "period_start", "period_end"),
    )

    id = Column(Integer, primary_key=True, index=True)
    platform_id = Column(Integer, ForeignKey("gig_platforms.id", ondelete="CASCADE"), nullable=False)
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)

    # Earnings breakdown
    gross_earnings = Column(Float, nullable=True)
    net_earnings = Column(Float, nullable=True)
    platform_fees = Column(Float, nullable=True)
    tips = Column(Float, nullable=True)
    bonuses = Column(Float, nullable=True)

    # Statistics
    trips_count = Column(Integer, nullable=True)
    total_distance = Column(Float, nullable=True)
    total_duration = Column(Integer, nullable=True)  # in seconds

    # Additional data
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    platform = relationship("GigPlatform", back_populates="earnings")