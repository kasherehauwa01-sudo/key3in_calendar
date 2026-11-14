import secrets
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_session
from app.models import TelegramLink, TelegramLinkRequest, User
from app.services.auth import current_user
from app.services.telegram_link import enabled, is_pending, lock_user, now_utc, token_hash

router = APIRouter(prefix="/api/users/me/telegram", tags=["telegram"])


@router.get("")
async def status(response: Response, user: User = Depends(current_user), session: AsyncSession = Depends(get_session)):
    response.headers["Cache-Control"] = "no-store"
    return {
        "available": enabled(get_settings()),
        "connected": await session.get(TelegramLink, user.id) is not None,
        "pending": is_pending(await session.get(TelegramLinkRequest, user.id)),
    }


@router.post("/connect")
async def connect(response: Response, user: User = Depends(current_user), session: AsyncSession = Depends(get_session)):
    settings = get_settings()
    if not enabled(settings):
        raise HTTPException(503, "Подключение Telegram пока недоступно")
    await lock_user(session, user.id)
    if await session.get(TelegramLink, user.id):
        raise HTTPException(409, "Telegram уже подключён")
    token = secrets.token_urlsafe(32)
    await session.merge(TelegramLinkRequest(
        user_id=user.id, token_hash=token_hash(token), expires_at=now_utc() + timedelta(minutes=10),
    ))
    await session.commit()
    response.headers["Cache-Control"] = "no-store"
    return {"url": f"https://t.me/{settings.telegram_bot_username}?start={token}"}


@router.delete("", status_code=204)
async def disconnect(user: User = Depends(current_user), session: AsyncSession = Depends(get_session)):
    await lock_user(session, user.id)
    for model in (TelegramLinkRequest, TelegramLink):
        row = await session.get(model, user.id)
        if row is not None:
            await session.delete(row)
    await session.commit()
    return Response(status_code=204)
