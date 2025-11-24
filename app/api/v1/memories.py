"""
Memory API endpoints - Quản lý ký ức
"""
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.core.database import get_db
from app.models.model_user import User
from app.models.model_diary import Memory, Diary
from app.models.model_user_profile import UserProfile
from app.schemas.sche_diary import MemoryCreate, MemoryResponse
from app.services.srv_ai import AIService
from app.services.srv_storage import StorageService
from app.utils.login_manager import login_required

router = APIRouter(prefix="/memory", tags=["💭 Memory"])


@router.post("/photo_audio", response_model=MemoryResponse)
async def save_memory_photo(
    image: UploadFile = File(...),
    audio: Optional[UploadFile] = File(None),
    content: str = Form(...),
    tags: str = Form(default="[]"),
    current_user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    """
    Lưu ảnh ký ức kèm âm thanh chú thích
    
    - **image**: File ảnh gia đình, con cháu, sự kiện
    - **audio**: File âm thanh chú thích (MP3, WAV, M4A) - tùy chọn
    - **content**: Mô tả văn bản (vd: "Đây là cháu đích tôn Bi, ảnh chụp hồi Tết năm 2023")
    - **tags**: Danh sách tags (JSON array string, vd: ["gia đình", "tết 2023"])
    """
    try:
        # Validate image
        if not StorageService.validate_file_type(image.content_type, ('image/',)):
            raise HTTPException(status_code=400, detail="File phải là ảnh")
        
        # Save image
        image_contents = await image.read()
        image_url = await StorageService.save_image(
            image_contents, 
            image.content_type, 
            current_user.id
        )
        
        # Save audio if provided
        audio_url = None
        if audio:
            if not StorageService.validate_file_type(audio.content_type, ('audio/',)):
                raise HTTPException(status_code=400, detail="File âm thanh không hợp lệ")
            
            audio_contents = await audio.read()
            audio_url = await StorageService.save_audio(
                audio_contents,
                audio.content_type,
                current_user.id
            )
        
        # Parse tags
        try:
            tags_list = json.loads(tags) if tags else []
        except json.JSONDecodeError:
            tags_list = []
        
        # Create memory
        memory = Memory(
            user_id=current_user.id,
            content=content,
            tags=json.dumps(tags_list, ensure_ascii=False),
            image_url=image_url,
            audio_url=audio_url
        )
        
        db.add(memory)
        db.commit()
        db.refresh(memory)
        
        # Convert tags back to list for response
        memory.tags = tags_list
        
        return memory
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi lưu ký ức: {str(e)}")


@router.post("", response_model=MemoryResponse)
async def save_memory(
    memory_data: MemoryCreate,
    current_user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    """Lưu ký ức (chỉ văn bản, không có ảnh/âm thanh)"""
    memory = Memory(
        user_id=current_user.id,
        content=memory_data.content,
        tags=json.dumps(memory_data.tags, ensure_ascii=False)
    )
    
    db.add(memory)
    db.commit()
    db.refresh(memory)
    
    # Convert tags to list for response
    memory.tags = memory_data.tags
    
    return memory


@router.get("", response_model=List[MemoryResponse])
async def list_memories(
    limit: int = 10,
    current_user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách ký ức
    
    Trả về ảnh gia đình, con cháu kèm audio chú thích (nếu có)
    """
    memories = db.query(Memory).filter(
        Memory.user_id == current_user.id
    ).order_by(Memory.created_at.desc()).limit(limit).all()
    
    # Convert tags from JSON string to list
    for memory in memories:
        if isinstance(memory.tags, str):
            try:
                memory.tags = json.loads(memory.tags)
            except json.JSONDecodeError:
                memory.tags = []
    
    return memories


@router.get("/prompt")
async def get_memory_prompt(
    current_user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    """Gợi ý hồi tưởng cá nhân hóa"""
    diaries = db.query(Diary).filter(
        Diary.user_id == current_user.id
    ).order_by(Diary.created_at.desc()).limit(10).all()
    
    memories = db.query(Memory).filter(
        Memory.user_id == current_user.id
    ).order_by(Memory.created_at.desc()).limit(10).all()
    
    user_profile = None
    try:
        user_profile = db.query(UserProfile).filter(
            UserProfile.user_id == current_user.id
        ).first()
    except Exception as e:
        print(f"Warning: Could not load user profile: {e}", flush=True)
    
    if not diaries and not memories:
        return {
            "success": True,
            "prompt": "Chào bác! Hôm nay bác có muốn kể cho cháu nghe về kỷ niệm đẹp nào từ tuổi thơ không ạ?",
            "note": "Chưa có dữ liệu"
        }
    
    prompt_text = await AIService.generate_memory_prompt_text(diaries, memories, user_profile)
    
    return {
        "success": True,
        "prompt": prompt_text or "Bác có nhớ món ăn yêu thích hồi nhỏ không ạ?",
        "based_on": {
            "diary_count": len(diaries),
            "memory_count": len(memories),
            "has_profile": user_profile is not None
        }
    }
