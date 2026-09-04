import base64
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database import get_session
from app.models import Session, User

bearer = HTTPBearer(auto_error=False)

def hash_pin(pin: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    digest = hashlib.scrypt(pin.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"{base64.b64encode(salt).decode()}:{base64.b64encode(digest).decode()}"

def verify_pin(pin: str, encoded: str) -> bool:
    try:
        salt_text, digest_text = encoded.split(":", 1)
        candidate = hash_pin(pin, base64.b64decode(salt_text)).split(":", 1)[1]
        return hmac.compare_digest(candidate, digest_text)
    except (ValueError, TypeError):
        return False

async def create_session(session: AsyncSession, user: User) -> str:
    token = secrets.token_urlsafe(48)
    session.add(Session(token=token, user_id=user.id, expires_at=datetime.now(timezone.utc) + timedelta(days=90)))
    await session.commit()
    return token

async def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), session: AsyncSession = Depends(get_session)) -> User:
    if not credentials:
        raise HTTPException(401, "Требуется вход")
    statement = select(Session).options(selectinload(Session.user)).where(Session.token == credentials.credentials)
    auth_session = await session.scalar(statement)
    if not auth_session:
        raise HTTPException(401, "Сессия истекла")
    expires_at = auth_session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(401, "Сессия истекла")
    return auth_session.user
