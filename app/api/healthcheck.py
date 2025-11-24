"""
Health Check API - Kiểm tra trạng thái dịch vụ
"""
from fastapi import APIRouter

from app.schemas.sche_response import BaseResponse

router = APIRouter(prefix="/health-check", tags=["❤️ Health Check"])


@router.get("", response_model=BaseResponse)
async def get():
    """Kiểm tra dịch vụ hoạt động"""
    return BaseResponse(http_code=200, message="OK")
