"""
Schemas for Diary, Note, Memory features
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Union
from datetime import datetime


# ========== DIARY SCHEMAS ==========

class DiaryCreate(BaseModel):
    content: str = Field(..., description="Nội dung nhật ký")
    entry_type: str = Field(default="diary", description="Loại: diary hoặc note")
    auto_analyze: bool = Field(default=True, description="Tự động phân tích bằng AI")


class DiaryResponse(BaseModel):
    id: int
    user_id: int
    content: str
    summary: Optional[str]
    emotion: Optional[str]
    image_url: Optional[str]
    entry_type: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== NOTE SCHEMAS ==========

class NoteCreate(BaseModel):
    content: str = Field(..., description="Nội dung ghi chú")
    auto_analyze: bool = Field(default=True, description="Tự động phân tích bằng AI")


class NoteResponse(BaseModel):
    id: int
    user_id: int
    content: str
    category: Optional[str]
    extracted_datetime: Optional[datetime]
    priority: Optional[str]
    is_reminder: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NoteAnalysisResponse(BaseModel):
    note: NoteResponse
    analysis: Optional[Dict]
    reminders_created: int
    reminders: List[Dict]


# ========== REMINDER SCHEMAS ==========

class ReminderCreate(BaseModel):
    title: str = Field(..., description="Tiêu đề nhắc nhở")
    description: Optional[str] = Field(None, description="Mô tả chi tiết")
    remind_at: datetime = Field(..., description="Thời gian nhắc nhở")
    note_id: Optional[int] = Field(None, description="ID ghi chú liên quan")


class ReminderResponse(BaseModel):
    id: int
    user_id: int
    note_id: Optional[int]
    title: str
    description: Optional[str]
    remind_at: datetime
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReminderUpdate(BaseModel):
    is_completed: bool = Field(..., description="Trạng thái hoàn thành")


# ========== MEMORY SCHEMAS ==========

class MemoryCreate(BaseModel):
    content: str = Field(..., description="Nội dung ký ức")
    tags: List[str] = Field(default_factory=list, description="Danh sách tags")


class MemoryResponse(BaseModel):
    id: int
    user_id: int
    content: str
    tags: List[str]
    image_url: Optional[str]
    audio_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
    
    @classmethod
    def model_validate(cls, obj, **kwargs):
        """Oracle compatibility: Convert tags JSON string to list"""
        import json
        if hasattr(obj, 'tags') and isinstance(obj.tags, str):
            try:
                obj.tags = json.loads(obj.tags)
            except:
                obj.tags = []
        return super().model_validate(obj, **kwargs)


# ========== HEALTH LOG SCHEMAS ==========

class HealthLogCreate(BaseModel):
    log_type: str = Field(..., description="Loại: blood_pressure, blood_sugar, weight, medication, symptom")
    value: str = Field(..., description="Giá trị")
    note: Optional[str] = Field(None, description="Ghi chú thêm")


class HealthLogResponse(BaseModel):
    id: int
    user_id: int
    log_type: str
    value: str
    note: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== CONVERSATION SCHEMAS ==========

class ChatMessage(BaseModel):
    message: str = Field(..., description="Tin nhắn gửi đến AI")


class ChatResponse(BaseModel):
    success: bool
    response: str
    conversation_id: int


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    messages: List[Dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== USER PROFILE SCHEMAS ==========

class UserProfileCreate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    birth_date: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    medical_conditions: List[str] = Field(default_factory=list)
    medications: List[Dict] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    hobbies: List[str] = Field(default_factory=list)
    important_dates: List[Dict] = Field(default_factory=list)
    daily_routine: Optional[str] = None


class UserProfileResponse(BaseModel):
    id: int
    user_id: int
    full_name: Optional[str]
    age: Optional[int]
    birth_date: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    emergency_contact: Optional[str]
    medical_conditions: List[str]
    medications: List[Dict]
    allergies: List[str]
    hobbies: List[str]
    important_dates: List[Dict]
    daily_routine: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== OCR SCHEMAS ==========

class OCRResponse(BaseModel):
    success: bool
    filename: str
    text: str
    length: int
