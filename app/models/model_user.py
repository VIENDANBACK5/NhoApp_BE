from sqlalchemy import Column, String, Integer, Float, Text
# from sqlalchemy.dialects.postgresql import ARRAY  # PostgreSQL only
from sqlalchemy.orm import relationship
import json

from app.models.model_base import BareBaseModel


class User(BareBaseModel):
    
    __tablename__ = "users"
    
    sso_sub = Column(String(255), unique=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    dob = Column(Float, index=True)
    gender = Column(String(50), index=True)
    first_name = Column(String(100), index=True)
    last_name = Column(String(100), index=True)
    full_name = Column(String(255), index=True)
    phone = Column(String(20), index=True)
    address = Column(String(500), index=True)
    identity_card = Column(String(50), index=True)
    identity_card_date = Column(Float, index=True)
    identity_card_place = Column(String(255), index=True)
    is_active = Column(Integer, default=1)  # Oracle: 1=True, 0=False (was Boolean)
    last_login = Column(Float)
    hashed_password = Column(String(255))
    roles = Column(Text, default='[]')  # Oracle: Store as JSON string (was ARRAY)
    
    # Helper methods for roles (Oracle compatibility)
    def get_roles(self):
        """Get roles as list from JSON string"""
        if isinstance(self.roles, str):
            return json.loads(self.roles) if self.roles else []
        return self.roles or []
    
    def set_roles(self, roles_list):
        """Set roles from list to JSON string"""
        self.roles = json.dumps(roles_list) if isinstance(roles_list, list) else roles_list
    
    # Relationships for new features
    diaries = relationship("Diary", back_populates="user", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    health_logs = relationship("HealthLog", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
