"""
OCR API endpoints - Trích xuất text từ ảnh
"""
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException

from app.models.model_user import User
from app.schemas.sche_diary import OCRResponse
from app.services.srv_ocr import OCRService
from app.utils.login_manager import login_required

router = APIRouter(prefix="/ocr", tags=["📸 OCR"])


@router.post("", response_model=OCRResponse)
async def extract_text_from_image(
    file: UploadFile = File(...),
    current_user: User = Depends(login_required)
):
    """Trích xuất text từ ảnh bằng OCR"""
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File phải là ảnh")
        
        contents = await file.read()
        extracted_text = await OCRService.extract_text_from_image(contents)
        
        return OCRResponse(
            success=True,
            filename=file.filename,
            text=extracted_text,
            length=len(extracted_text)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý ảnh: {str(e)}")
