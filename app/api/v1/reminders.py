"""
Reminder API endpoints - Quản lý nhắc nhở
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.model_user import User
from app.models.model_diary import Reminder
from app.schemas.sche_diary import ReminderCreate, ReminderResponse, ReminderUpdate
from app.utils.login_manager import login_required

router = APIRouter(prefix="/reminder", tags=["⏰ Reminder"])


@router.post("", response_model=ReminderResponse)
async def create_reminder(
    reminder_data: ReminderCreate,
    current_user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    """Tạo nhắc nhở thủ công"""
    # Convert reminder data and handle note_id for Oracle foreign key
    reminder_dict = reminder_data.dict()
    
    # Remove note_id if it's None or 0 to avoid foreign key constraint error
    note_id = reminder_dict.get('note_id')
    if note_id is None or note_id == 0:
        reminder_dict.pop('note_id', None)
    
    reminder = Reminder(
        user_id=current_user.id,
        **reminder_dict
    )
    
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    
    return reminder


@router.get("", response_model=List[ReminderResponse])
async def list_reminders(
    status: str = "pending",
    current_user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    """Lấy danh sách nhắc nhở"""
    query = db.query(Reminder).filter(Reminder.user_id == current_user.id)
    
    if status == "pending":
        query = query.filter(Reminder.is_completed == False)
    
    reminders = query.order_by(Reminder.remind_at).all()
    return reminders


@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: int,
    update_data: ReminderUpdate,
    current_user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    """Cập nhật trạng thái nhắc nhở"""
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == current_user.id
    ).first()
    
    if not reminder:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhắc nhở")
    
    reminder.is_completed = update_data.is_completed
    db.commit()
    db.refresh(reminder)
    
    return reminder
