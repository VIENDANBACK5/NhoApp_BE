"""
Health API endpoints - Quản lý sức khỏe
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.models.model_user import User
from app.models.model_diary import HealthLog
from app.models.model_user_profile import UserProfile
from app.schemas.sche_diary import HealthLogCreate, HealthLogResponse
from app.services.srv_ai import AIService
from app.utils.login_manager import login_required

router = APIRouter(prefix="/health", tags=["🏥 Health"])


@router.post("/logs", response_model=HealthLogResponse)
async def log_health(
    health_data: HealthLogCreate,
    current_user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    """Ghi nhật ký sức khỏe"""
    health_log = HealthLog(
        user_id=current_user.id,
        **health_data.dict()
    )
    
    db.add(health_log)
    db.commit()
    db.refresh(health_log)
    
    return health_log


@router.get("/logs", response_model=List[HealthLogResponse])
async def list_health_logs(
    limit: int = 10,
    current_user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    """Lấy nhật ký sức khỏe"""
    logs = db.query(HealthLog).filter(
        HealthLog.user_id == current_user.id
    ).order_by(HealthLog.created_at.desc()).limit(limit).all()
    
    return logs


@router.get("/insights")
async def health_insights(
    current_user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    """Phân tích xu hướng sức khỏe bằng AI"""
    health_logs = db.query(HealthLog).filter(
        HealthLog.user_id == current_user.id
    ).order_by(HealthLog.created_at.desc()).limit(30).all()
    
    if not health_logs:
        return {
            "success": True,
            "insights": "Chưa có dữ liệu sức khỏe để phân tích.",
            "suggestion": "Hãy bắt đầu ghi chép các thông số sức khỏe hàng ngày!"
        }
    
    # Fix: Only query if needed, handle None case
    user_profile = None
    try:
        user_profile = db.query(UserProfile).filter(
            UserProfile.user_id == current_user.id
        ).first()
    except Exception:
        pass
    
    insights = await AIService.analyze_health_trend(health_logs, user_profile)
    
    return {
        "success": True,
        "total_logs": len(health_logs),
        "insights": insights or "Không thể phân tích lúc này.",
        "recent_logs": [
            {
                "log_type": log.log_type,
                "value": log.value,
                "created_at": datetime.fromtimestamp(log.created_at).isoformat() if isinstance(log.created_at, (int, float)) else log.created_at.isoformat()
            }
            for log in health_logs[:5]
        ]
    }
