from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select
from app.db.session import get_session
from app.db.datamodels import User, Token
from app.utils.security import verify_password, create_access_token
from app.config import settings
from datetime import timedelta

router = APIRouter()

# --- Custom Login Schema ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/login", response_model=Token)
async def login_for_access_token(
    login_data: LoginRequest,
    session: Annotated[Session, Depends(get_session)]
):
    """
    Login with Email and Password (JSON Body).
    """
    # 1. Find User by Email
    user = session.exec(select(User).where(User.email == login_data.email)).first()
    
    # 2. Verify Password
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Create Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")