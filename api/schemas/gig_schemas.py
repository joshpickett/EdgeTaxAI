from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

class PlatformType(str, Enum):
    UBER = "uber"
    LYFT = "lyft"
    DOORDASH = "doordash"
    INSTACART = "instacart"

class PlatformStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ERROR = "error"

class GigPlatformBase(BaseModel):
    platform: PlatformType
    platform_user_id: Optional[str]
    platform_email: Optional[str]
    is_active: bool = True
    account_status: PlatformStatus = PlatformStatus.PENDING
    metadata: Optional[Dict[str, Any]]
    error_message: Optional[str]

class GigPlatformCreate(GigPlatformBase):
    access_token: str
    refresh_token: Optional[str]

class GigPlatformUpdate(BaseModel):
    platform_email: Optional[str]
    is_active: Optional[bool]
    metadata: Optional[Dict[str, Any]]

    class Config:
        orm_mode = True

class GigEarningsBase(BaseModel):
    platform_id: int
    period_start: datetime
    period_end: datetime
    gross_earnings: float
    net_earnings: float
    trips_count: int
    metadata: Optional[Dict[str, Any]]

class GigEarningsCreate(GigEarningsBase):
    pass

class GigEarningsResponse(GigEarningsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class GigPlatformResponse(GigPlatformBase):
    id: int
    user_id: int
    last_sync: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
