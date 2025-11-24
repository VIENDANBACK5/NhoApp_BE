"""
Authentication API endpoints - Đăng nhập, đăng ký
"""
from typing import Any

from fastapi import APIRouter, Depends

from app.schemas.sche_response import DataResponse
from app.services.srv_auth import AuthService
from app.utils.exception_handler import CustomException
from app.schemas.sche_auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.sche_user import UserBaseResponse

router = APIRouter(prefix="/auth", tags=["🔐 Authentication"])


@router.post("/login", response_model=DataResponse[TokenResponse])
def login_basic(form_data: LoginRequest, auth_service: AuthService = Depends()):
    """Đăng nhập cơ bản"""
    try:
        token = auth_service.login(data=form_data)
        return DataResponse(http_code=200, data=token)
    except Exception as e:
        print(e, flush=True)
        raise CustomException(exception=e)


@router.post("/register", response_model=DataResponse[UserBaseResponse])
def register(data: RegisterRequest, auth_service: AuthService = Depends()) -> Any:
    """Đăng ký tài khoản mới"""
    try:
        register_user = auth_service.register(data)
        print(register_user.email)
        return DataResponse(http_code=201, data=register_user)
    except Exception as e:
        raise CustomException(exception=e)
