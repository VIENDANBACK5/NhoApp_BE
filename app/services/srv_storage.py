import uuid
import aiohttp
from typing import Tuple
from datetime import datetime
from app.core.config import settings

class StorageService:
    @staticmethod
    async def save_image(file_content: bytes, content_type: str, user_id: int) -> str:
        # Lưu ảnh lên Cloudflare R2, trả về URL
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = content_type.split('/')[-1]
        filename = f"uploads/user_{user_id}/images/{timestamp}_{uuid.uuid4().hex[:8]}.{file_ext}"
        async with aiohttp.ClientSession() as session:
            upload_url_endpoint = f"{settings.R2_WORKER_URL}/generate-upload-url"
            params = {"fileName": filename, "contentType": content_type}
            async with session.get(upload_url_endpoint, params=params) as resp:
                if resp.status != 200:
                    raise Exception(f"Không lấy được upload URL: {await resp.text()}")
                data = await resp.json()
                presigned_url = data.get("uploadUrl")
            headers = {"Content-Type": content_type}
            async with session.put(presigned_url, data=file_content, headers=headers) as resp:
                if resp.status not in (200, 201, 204):
                    raise Exception(f"Upload thất bại: {await resp.text()}")
        return f"{settings.R2_BUCKET_URL}/{filename}"

    @staticmethod
    async def save_audio(file_content: bytes, content_type: str, user_id: int) -> str:
        # Lưu audio lên Cloudflare R2, trả về URL
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = content_type.split('/')[-1]
        filename = f"uploads/user_{user_id}/audio/{timestamp}_{uuid.uuid4().hex[:8]}.{file_ext}"
        async with aiohttp.ClientSession() as session:
            upload_url_endpoint = f"{settings.R2_WORKER_URL}/generate-upload-url"
            params = {"fileName": filename, "contentType": content_type}
            async with session.get(upload_url_endpoint, params=params) as resp:
                if resp.status != 200:
                    raise Exception(f"Không lấy được upload URL: {await resp.text()}")
                data = await resp.json()
                presigned_url = data.get("uploadUrl")
            headers = {"Content-Type": content_type}
            async with session.put(presigned_url, data=file_content, headers=headers) as resp:
                if resp.status not in (200, 201, 204):
                    raise Exception(f"Upload thất bại: {await resp.text()}")
        return f"{settings.R2_BUCKET_URL}/{filename}"

    @staticmethod
    async def delete_file(file_url: str) -> bool:
        # Xóa file khỏi R2
        try:
            filename = file_url.split("/bucket/files/")[-1]
            async with aiohttp.ClientSession() as session:
                delete_endpoint = f"{settings.R2_WORKER_URL}/delete-object"
                headers = {"Content-Type": "application/json"}
                payload = {"fileName": filename}
                async with session.post(delete_endpoint, json=payload, headers=headers) as resp:
                    return resp.status == 200
        except Exception as e:
            print(f"Lỗi xóa file: {e}")
            return False

    @staticmethod
    def validate_file_type(content_type: str, allowed_types: Tuple[str, ...]) -> bool:
        return any(content_type.startswith(t) for t in allowed_types)
