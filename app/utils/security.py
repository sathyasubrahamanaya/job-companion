from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import jwt
from passlib.context import CryptContext
from app.config import settings

# FIX: Use "bcrypt_sha256" instead of plain "bcrypt".
# This pre-hashes the password with SHA256 before passing it to bcrypt.
# It solves the 72-byte limit while keeping compatibility with standard bcrypt hashes.
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if the typed password matches the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Scrambles the password before saving to DB."""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generates the JWT string."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Default to 15 minutes if not specified
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    # Add Expiration Claim
    to_encode.update({"exp": expire})
    
    # Create the Token
    algorithm = str(settings.ALGORITHM)
    secret_key = str(settings.SECRET_KEY)

    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt