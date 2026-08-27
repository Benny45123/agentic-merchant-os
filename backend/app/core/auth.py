from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional
import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.enums import UserRole

security_scheme = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    sub: str
    role: str

    @property
    def is_buyer(self) -> bool:
        return self.role == UserRole.BUYER.value

    @property
    def is_merchant(self) -> bool:
        return self.role == UserRole.MERCHANT.value


def create_access_token(
    sub: str,
    role: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    settings = get_settings()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)

    to_encode: Dict[str, Any] = {
        "sub": sub,
        "role": role,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SIGNING_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SIGNING_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme)
) -> CurrentUser:
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    payload = decode_access_token(token)
    sub = payload.get("sub")
    role = payload.get("role")
    if not sub or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing sub or role",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return CurrentUser(sub=sub, role=role)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme)
) -> Optional[CurrentUser]:
    if credentials is None or not credentials.credentials:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        sub = payload.get("sub")
        role = payload.get("role")
        if sub and role:
            return CurrentUser(sub=sub, role=role)
    except HTTPException:
        return None
    return None
