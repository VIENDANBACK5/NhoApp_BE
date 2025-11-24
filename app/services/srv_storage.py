import base64
import uuid
from typing import Optional, Tuple
from datetime import datetime


class StorageService:
    @staticmethod
    async def save_image(file_content: bytes, content_type: str, user_id: int) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = content_type.split('/')[-1]
        filename = f"user_{user_id}/images/{timestamp}_{uuid.uuid4().hex[:8]}.{file_ext}"
        
        image_base64 = base64.b64encode(file_content).decode('utf-8')
        return f"data:{content_type};base64,{image_base64}"
    
    @staticmethod
    async def save_audio(file_content: bytes, content_type: str, user_id: int) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = content_type.split('/')[-1]
        filename = f"user_{user_id}/audio/{timestamp}_{uuid.uuid4().hex[:8]}.{file_ext}"
        
        audio_base64 = base64.b64encode(file_content).decode('utf-8')
        return f"data:{content_type};base64,{audio_base64}"
    
    @staticmethod
    def validate_file_type(content_type: str, allowed_types: Tuple[str, ...]) -> bool:
        return any(content_type.startswith(t) for t in allowed_types)
