from typing import Annotated
from fastapi import Depends, HTTPException, status
# 1. Change Import
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials 
from jose import JWTError, jwt
from sqlmodel import Session, select
from app.db.session import get_session
from app.db.datamodels import User, TokenData
from app.config import settings

# 2. Change Scheme
security = HTTPBearer()

async def get_current_user(
    # 3. Update Dependency to extract token from header
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[Session, Depends(get_session)]
) -> User:
    token = credentials.credentials # Extract "Bearer <token>"
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email_raw = payload.get("sub")
        if email_raw is None:
            raise credentials_exception
            
        token_data = TokenData(email=str(email_raw))
        
    except JWTError:
        raise credentials_exception

    if token_data.email is None:
         raise credentials_exception

    user = session.exec(select(User).where(User.email == token_data.email)).first()
    if user is None:
        raise credentials_exception
        
    return user