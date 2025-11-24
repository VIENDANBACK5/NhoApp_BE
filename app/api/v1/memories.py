from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.core.database import get_db
from app.models.model_user import User
from app.models.model_diary import Memory, Diary
from app.models.model_user_profile import UserProfile
from app.schemas.sche_diary import MemoryCreate, MemoryUpdate, MemoryResponse
from app.services.srv_ai import AIService
from app.services.srv_storage import StorageService
from app.utils.login_manager import login_required

router = APIRouter(prefix="/memory", tags=["Memory"])


@router.post("/photo_audio", response_model=MemoryResponse)
async def save_memory_photo(
    image: UploadFile = File(...),
    audio: Optional[UploadFile] = File(None),
    content: str = Form(...),
    tags: str = Form(default="[]"),
    current_user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    try:
        if not StorageService.validate_file_type(image.content_type, ('image/',)):
            raise HTTPException(status_code=400, detail="File phải là ảnh")
        
        image_contents = await image.read()
        image_url = await StorageService.save_image(
            image_contents, 
            image.content_type, 
            current_user.id
        )
        
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
        
        try:
            tags_list = json.loads(tags) if tags else []
        except json.JSONDecodeError:
            tags_list = []
        
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
    memory = Memory(
        user_id=current_user.id,
        content=memory_data.content,
        tags=json.dumps(memory_data.tags, ensure_ascii=False)
    )
    
    db.add(memory)
    db.commit()
    db.refresh(memory)
    
    memory.tags = memory_data.tags
    
    return memory


@router.get("", response_model=List[MemoryResponse])
async def list_memories(
    limit: int = 10,
    current_user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    memories = db.query(Memory).filter(
        Memory.user_id == current_user.id
    ).order_by(Memory.created_at.desc()).limit(limit).all()
    
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


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: int,
    current_user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    memory = db.query(Memory).filter(
        Memory.id == memory_id,
        Memory.user_id == current_user.id
    ).first()
    
    if not memory:
        raise HTTPException(status_code=404, detail="Không tìm thấy ký ức")
    
    if isinstance(memory.tags, str):
        try:
            memory.tags = json.loads(memory.tags)
        except:
            memory.tags = []
    
    return memory


@router.put("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: int,
    update_data: MemoryUpdate,
    current_user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    memory = db.query(Memory).filter(
        Memory.id == memory_id,
        Memory.user_id == current_user.id
    ).first()
    
    if not memory:
        raise HTTPException(status_code=404, detail="Không tìm thấy ký ức")
    
    if update_data.content is not None:
        memory.content = update_data.content
    
    if update_data.tags is not None:
        memory.tags = json.dumps(update_data.tags, ensure_ascii=False)
    
    db.commit()
    db.refresh(memory)
    if isinstance(memory.tags, str):
        try:
            memory.tags = json.loads(memory.tags)
        except:
            memory.tags = []
    
    return memory


@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: int,
    current_user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    memory = db.query(Memory).filter(
        Memory.id == memory_id,
        Memory.user_id == current_user.id
    ).first()
    
    if not memory:
        raise HTTPException(status_code=404, detail="Không tìm thấy ký ức")
    
    db.delete(memory)
    db.commit()
    
    return {
        "success": True,
        "message": "Đã xóa ký ức",
        "deleted_id": memory_id
    }
