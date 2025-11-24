"""  
Diary, Note, Memory Models
"""
import json
from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.model_base import BareBaseModel
class Diary(BareBaseModel):
    """Nhật ký cá nhân"""
    __tablename__ = "diaries"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    emotion = Column(String(50), nullable=True)
    image_url = Column(String(500), nullable=True)
    entry_type = Column(String(20), default="diary")  # diary or note
    
    # Relationships
    user = relationship("User", back_populates="diaries")


class Note(BareBaseModel):
    """Ghi chú thông minh"""
    __tablename__ = "notes"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=True)  # medication, event, appointment, task, health, other
    extracted_datetime = Column(DateTime, nullable=True)
    priority = Column(String(20), default="medium")  # high, medium, low
    is_reminder = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="notes")
    reminders = relationship("Reminder", back_populates="note", cascade="all, delete-orphan")


class Reminder(BareBaseModel):
    """Nhắc nhở tự động"""
    __tablename__ = "reminders"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    remind_at = Column(DateTime, nullable=False)
    is_completed = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="reminders")
    note = relationship("Note", back_populates="reminders")


class Memory(BareBaseModel):
    """Ký ức cá nhân"""
    __tablename__ = "memories"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(Text, default='[]')  # List of tags (JSON string for Oracle)
    image_url = Column(String(500), nullable=True)  # URL ảnh gia đình, con cháu
    audio_url = Column(String(500), nullable=True)  # URL file âm thanh chú thích
    
    # Relationships
    user = relationship("User", back_populates="memories")
    
    @property
    def tags_list(self):
        try:
            return json.loads(self.tags) if self.tags else []
        except:
            return []
    
    @tags_list.setter
    def tags_list(self, value):
        self.tags = json.dumps(value) if isinstance(value, list) else value


class HealthLog(BareBaseModel):
    """Nhật ký sức khỏe"""
    __tablename__ = "health_logs"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    log_type = Column(String(50), nullable=False)  # blood_pressure, blood_sugar, weight, medication, symptom
    value = Column(String(100), nullable=False)
    note = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="health_logs")


class Conversation(BareBaseModel):
    """Lịch sử chat với AI"""
    __tablename__ = "conversations"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    messages = Column(Text, default='[]')  # [{"role": "user/assistant", "content": "..."}] (JSON string for Oracle)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    
    @property
    def messages_list(self):
        try:
            return json.loads(self.messages) if self.messages else []
        except:
            return []
    
    @messages_list.setter
    def messages_list(self, value):
        self.messages = json.dumps(value) if isinstance(value, list) else value
