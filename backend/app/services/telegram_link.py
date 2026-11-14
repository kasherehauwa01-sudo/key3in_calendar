import asyncio
import hashlib
import logging
import re
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.config import get_settings
from app.database import SessionLocal
from app.models import TelegramLink, TelegramLinkRequest, User
from app.services.telegram import TelegramError, bot_request

log = logging.getLogger(__name__)
START = re.compile(r"/start(?:@[A-Za-z0-9_]+)? ([A-Za-z0-9_-]{43})")


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("ascii")).hexdigest()


def now_utc():
    return datetime.now(timezone.utc)


def is_pending(request) -> bool:
    return request is not None and request.expires_at.replace(tzinfo=timezone.utc) > now_utc()


def enabled(settings) -> bool:
    return bool(settings.telegram_bot_token.get_secret_value() and settings.telegram_bot_username)


async def lock_user(session, user_id):
    return await session.scalar(select(User.id).where(User.id == user_id).with_for_update())


async def link_update(session, message):
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    if chat.get("type") != "private" or type(chat_id) is not int or chat_id <= 0:
        return None
    match = START.fullmatch(message.get("text") or "")
    if not match:
        return None

    digest = token_hash(match[1])
    user_id = await session.scalar(
        select(TelegramLinkRequest.user_id).where(TelegramLinkRequest.token_hash == digest)
    )
    if user_id is None or await lock_user(session, user_id) is None:
        return chat_id, "Ссылка недействительна. Откройте настройки календаря и запросите новую."

    request = await session.get(TelegramLinkRequest, user_id)
    if not is_pending(request) or request.token_hash != digest:
        return chat_id, "Ссылка недействительна. Откройте настройки календаря и запросите новую."

    existing = await session.get(TelegramLink, user_id)
    if existing is not None and existing.chat_id != chat_id:
        return chat_id, "Аккаунт календаря уже подключён к другому чату."
    if existing is None:
        session.add(TelegramLink(user_id=user_id, chat_id=chat_id))
    await session.delete(request)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        return chat_id, "Этот чат уже привязан к другому аккаунту календаря."
    return chat_id, "Telegram подключён. Теперь сюда будут приходить уведомления о новых событиях."


async def run_link_worker():
    settings = get_settings()
    offset = None
    failures = 0

    async def request(method, payload):
        return await asyncio.to_thread(
            bot_request, settings.telegram_bot_token.get_secret_value(),
            settings.telegram_proxy_url.get_secret_value(), method, payload,
        )

    while True:
        try:
            params = {"timeout": 5, "allowed_updates": ["message"]}
            if offset is not None:
                params["offset"] = offset
            for update in await request("getUpdates", params):
                async with SessionLocal() as session:
                    reply = await link_update(session, update.get("message") or {})
                if reply:
                    chat_id, message = reply
                    try:
                        await request("sendMessage", {
                            "chat_id": chat_id,
                            "text": message + ("\n\n" + settings.telegram_calendar_url if settings.telegram_calendar_url else ""),
                            "link_preview_options": {"is_disabled": True},
                        })
                    except TelegramError as error:
                        log.warning("Telegram link reply failed (code %s)", error.status)
                offset = update["update_id"] + 1
            failures = 0
        except Exception as error:
            failures += 1
            log.warning("Telegram link polling failed (%s, code %s)", type(error).__name__, getattr(error, "status", None))
            await asyncio.sleep(min(60, 2 ** min(failures, 6)))
