"""
Chat API endpoints - Trò chuyện với AI
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.model_user import User
from app.models.model_diary import Conversation
from app.models.model_user_profile import UserProfile
from app.schemas.sche_diary import ChatMessage, ChatResponse
from app.services.srv_ai import AIService
from app.utils.login_manager import login_required

router = APIRouter(prefix="/chat", tags=["💬 Chat AI"])


@router.post("", response_model=ChatResponse)
async def chat_with_ai(
    chat_data: ChatMessage,
    current_user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    """Chat với AI có ngữ cảnh"""
    try:
        # Get user profile - handle Oracle type conversion issues
        profile_dict = None
        try:
            user_profile = db.query(UserProfile).filter(
                UserProfile.user_id == current_user.id
            ).first()
            
            if user_profile:
                profile_dict = {
                    "full_name": user_profile.full_name,
                    "age": user_profile.age,
                    "hobbies": user_profile.hobbies or []
                }
        except Exception as profile_error:
            # Ignore profile errors, continue without profile context
            print(f"Warning: Could not load user profile: {profile_error}", flush=True)
            profile_dict = None
        
        # Get recent conversation
        recent_conv = db.query(Conversation).filter(
            Conversation.user_id == current_user.id
        ).order_by(Conversation.created_at.desc()).first()
        
        conversation_history = []
        if recent_conv:
            conversation_history = recent_conv.messages_list
        
        # AI chat
        response = await AIService.chat_with_context(
            chat_data.message,
            conversation_history,
            profile_dict
        )
        
        # Save conversation (convert list to JSON string for Oracle)
        conversation_history.append({"role": "user", "content": chat_data.message})
        conversation_history.append({"role": "assistant", "content": response})
        
        import json
        if recent_conv:
            recent_conv.messages = json.dumps(conversation_history, ensure_ascii=False)
            db.commit()
            conversation_id = recent_conv.id
        else:
            new_conv = Conversation(
                user_id=current_user.id,
                messages=json.dumps(conversation_history, ensure_ascii=False)
            )
            db.add(new_conv)
            db.commit()
            db.refresh(new_conv)
            conversation_id = new_conv.id
        
        return ChatResponse(
            success=True,
            response=response,
            conversation_id=conversation_id
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi chat: {str(e)}")
