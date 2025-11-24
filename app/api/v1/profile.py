"""
Profile API endpoints - Quản lý thông tin cá nhân
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from app.models.model_user import User
from app.models.model_user_profile import UserProfile
from app.schemas.sche_diary import UserProfileCreate, UserProfileResponse
from app.utils.login_manager import login_required

router = APIRouter(prefix="/profile", tags=["👤 Profile"])


@router.get("", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    """Lấy thông tin profile người dùng"""
    # Use direct SQL to avoid ORM issues with Oracle
    try:
        result = db.execute(
            text("SELECT * FROM user_profiles WHERE user_id = :user_id"),
            {"user_id": current_user.id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="Chưa có profile")
        
        # Convert Row to UserProfile object
        profile = UserProfile()
        for key in result._mapping.keys():
            setattr(profile, key, result._mapping[key])
        
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi truy vấn profile: {str(e)}")


@router.post("", response_model=UserProfileResponse)
async def create_or_update_profile(
    profile_data: UserProfileCreate,
    current_user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    """Tạo hoặc cập nhật profile"""
    try:
        # Check if profile exists using raw SQL
        result = db.execute(
            text("SELECT id FROM user_profiles WHERE user_id = :user_id"),
            {"user_id": current_user.id}
        ).first()
        
        if result:
            # Update existing profile
            update_fields = []
            params = {"user_id": current_user.id}
            
            for key, value in profile_data.dict(exclude_unset=True).items():
                update_fields.append(f"{key} = :{key}")
                params[key] = value
            
            if update_fields:
                query = f"UPDATE user_profiles SET {', '.join(update_fields)} WHERE user_id = :user_id"
                db.execute(text(query), params)
                db.commit()
        else:
            # Create new profile
            fields = ["user_id"] + list(profile_data.dict(exclude_unset=True).keys())
            values = [f":{field}" for field in fields]
            params = {"user_id": current_user.id, **profile_data.dict(exclude_unset=True)}
            
            query = f"INSERT INTO user_profiles ({', '.join(fields)}) VALUES ({', '.join(values)})"
            db.execute(text(query), params)
            db.commit()
        
        # Fetch and return the profile
        result = db.execute(
            text("SELECT * FROM user_profiles WHERE user_id = :user_id"),
            {"user_id": current_user.id}
        ).first()
        
        profile = UserProfile()
        for key in result._mapping.keys():
            setattr(profile, key, result._mapping[key])
        
        return profile
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi cập nhật profile: {str(e)}")
    
    return profile
