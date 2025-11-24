from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.models.model_user import User
from app.models.model_diary import Note, Reminder
from app.models.model_user_profile import UserProfile
from app.schemas.sche_diary import NoteCreate, NoteResponse, NoteAnalysisResponse
from app.services.srv_ocr import OCRService
from app.services.srv_ai import AIService
from app.utils.login_manager import login_required

router = APIRouter(prefix="/note", tags=["Note"])


@router.post("", response_model=NoteAnalysisResponse)
async def create_note_from_image(
    file: UploadFile = File(...),
    auto_analyze: bool = Form(True),
    current_user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File phải là ảnh")
        
        contents = await file.read()
        extracted_text = await OCRService.extract_text_from_image(contents)
        
        if not extracted_text:
            raise HTTPException(status_code=400, detail="Không đọc được text từ ảnh")
        
        profile_dict = None
        try:
            user_profile = db.query(UserProfile).filter(
                UserProfile.user_id == current_user.id
            ).first()
            
            if user_profile:
                profile_dict = {
                    "full_name": user_profile.full_name,
                    "age": user_profile.age,
                    "medical_conditions": user_profile.medical_conditions or [],
                    "medications": user_profile.medications or []
                }
        except Exception as e:
            print(f"Warning: Could not load user profile: {e}", flush=True)
            profile_dict = None
        
        analysis = None
        created_reminders = []
        
        if auto_analyze:
            analysis = await AIService.analyze_note(extracted_text, profile_dict)
            
            note = Note(
                user_id=current_user.id,
                content=extracted_text,
                category=analysis.get('category'),
                extracted_datetime=datetime.fromisoformat(analysis['extracted_datetime']) if analysis.get('extracted_datetime') else None,
                priority=analysis.get('priority'),
                is_reminder=analysis.get('should_create_reminder', False)
            )
            
            db.add(note)
            db.commit()
            db.refresh(note)
            
            if analysis.get('should_create_reminder'):
                reminder_dicts = AIService.generate_reminders_from_note(
                    note.id, extracted_text, analysis, current_user.id
                )
                
                for r_dict in reminder_dicts:
                    reminder = Reminder(**r_dict)
                    db.add(reminder)
                    created_reminders.append(reminder)
                
                db.commit()
        
        else:
            note = Note(
                user_id=current_user.id,
                content=extracted_text,
                category="other",
                priority="medium",
                is_reminder=False
            )
            db.add(note)
            db.commit()
            db.refresh(note)
        
        return NoteAnalysisResponse(
            note=note,
            analysis=analysis,
            reminders_created=len(created_reminders),
            reminders=[{
                "id": r.id,
                "title": r.title,
                "remind_at": r.remind_at.isoformat()
            } for r in created_reminders]
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi tạo ghi chú: {str(e)}")


@router.get("", response_model=List[NoteResponse])
async def list_notes(
    limit: int = 10,
    current_user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    notes = db.query(Note).filter(
        Note.user_id == current_user.id
    ).order_by(Note.created_at.desc()).limit(limit).all()
    
    return notes
