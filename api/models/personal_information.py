from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
from api.config.database import Base

class PersonalInformation(Base):
    __tablename__ = "personal_information"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(15), index=True)
    ssn = Column(String(11), unique=True, nullable=False)
    dob = Column(Date, nullable=False)
    address_line1 = Column(String(100), nullable=False)
    address_line2 = Column(String(100))
    city = Column(String(50), nullable=False)
    state = Column(String(2), nullable=False, 
                  CheckConstraint("LENGTH(state) = 2"))
    zip_code = Column(String(10), nullable=False)
    created_at = Column(DateTime(timezone=True), 
                       server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime(timezone=True), 
                       server_default=text('CURRENT_TIMESTAMP'),
                       onupdate=text('CURRENT_TIMESTAMP'))

    # Relationship
    user = relationship("Users", back_populates="personal_info", uselist=False)
