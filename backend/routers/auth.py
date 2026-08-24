import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from backend.config import settings
from backend.services.auth_service import (
    verify_password,
    create_access_token,
    get_current_admin,
)

logger = logging.getLogger("auth")

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: Dict[str, Any]


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """
    Authenticate single-operator admin using email & password.
    Returns a signed JWT bearer token.
    """
    provided_email = credentials.email.strip().lower()
    admin_email = settings.ADMIN_EMAIL.strip().lower()

    if provided_email != admin_email:
        logger.warning(f"Failed login attempt for unknown email: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    is_valid = verify_password(credentials.password, settings.ADMIN_PASSWORD_HASH)
    if not is_valid:
        logger.warning(f"Failed login attempt (invalid password) for: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_payload = {
        "sub": admin_email,
        "role": "admin",
        "name": "Operator"
    }

    access_token = create_access_token(data=user_payload)
    logger.info(f"Successful login for operator: {admin_email}")

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        user=user_payload
    )


@router.get("/me")
async def get_current_user_profile(
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """
    Returns current authenticated operator session information.
    """
    return {
        "authenticated": True,
        "user": current_admin
    }
