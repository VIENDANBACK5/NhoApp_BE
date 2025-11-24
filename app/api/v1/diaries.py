"""
Diary API endpoints - Quản lý nhật ký
"""
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form
from sqlalchemy.orm import Session
from typing import List
import base64

from app.core.database import get_db
from app.models.model_user import User
from app.models.model_diary import Diary
from app.schemas.sche_diary import DiaryCreate, DiaryResponse
from app.services.srv_ocr import OCRService
from app.services.srv_ai import AIService
from app.utils.login_manager import login_required

router = APIRouter(prefix="/diary", tags=["📔 Diary"])


@router.post("", response_model=DiaryResponse)
async def create_diary_from_image(
    file: UploadFile = File(...),
    auto_analyze: bool = Form(True),
    current_user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    """Tạo nhật ký từ ảnh với AI phân tích"""
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File phải là ảnh")
        
        # OCR
        contents = await file.read()
        extracted_text = await OCRService.extract_text_from_image(contents)
        
        if not extracted_text:
            raise HTTPException(status_code=400, detail="Không đọc được text từ ảnh")
        
        # Save image (giản lược: lưu base64 hoặc upload lên S3/storage)
        image_base64 = base64.b64encode(contents).decode('utf-8')
        
        # AI analysis
        emotion = None
        
        if auto_analyze:
            emotion = await AIService.analyze_emotion(extracted_text)
        
        # Create diary
        diary = Diary(
            user_id=current_user.id,
            content=extracted_text,
            summary=None,
            emotion=emotion,
            image_url=None,  # TODO: Upload to storage and save URL
            entry_type="diary"
        )
        
        db.add(diary)
        db.commit()
        db.refresh(diary)
        
        return diary
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi tạo nhật ký: {str(e)}")


@router.get("", response_model=List[DiaryResponse])
async def list_diaries(
    limit: int = 10,
    current_user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    """Lấy danh sách nhật ký"""
    diaries = db.query(Diary).filter(
        Diary.user_id == current_user.id
    ).order_by(Diary.created_at.desc()).limit(limit).all()
    
    return diaries
