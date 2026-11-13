import asyncio
import json
import logging
import re
from datetime import date, datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import SessionLocal
from app.models import TelegramDelivery, TelegramLink, User

log = logging.getLogger(__name__)


class TelegramError(Exception):
    def __init__(self, status: int | None = None, retry_after: int = 0):
        self.status = status
        self.retry_after = retry_after


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def bot_request(token: str, proxy: str, method: str, payload: dict):
    if not re.fullmatch(r"[0-9]+:[A-Za-z0-9_-]+", token):
        raise TelegramError(401)
    opener = build_opener(ProxyHandler({"https": proxy} if proxy else {}), NoRedirect())
    request = Request(
        f"https://api.telegram.org/bot{token}/{method}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    status = None
    try:
        try:
            with opener.open(request, timeout=8) as response:
                data = json.load(response)
        except HTTPError as error:
            status = error.code
            with error:
                data = json.load(error)
        if data.get("ok") is True and status is None:
            return data["result"]
        code = data.get("error_code")
        retry_after = data.get("parameters", {}).get("retry_after", 0)
        # Only a Bot API response (not a proxy's generic HTTP error) is permanent.
        raise TelegramError(code if type(code) is int else None, retry_after if type(retry_after) is int else 0)
    except (URLError, OSError, ValueError, KeyError, AttributeError, TypeError):
        raise TelegramError() from None


async def enqueue_created(session: AsyncSession, author: User, day: date, body: str, *, recurring=False):
    settings = get_settings()
    if not settings.telegram_bot_token.get_secret_value():
        return
    subject = "Новое повторяющееся событие" if recurring else "Новое событие"
    header = f"{subject} в Key3in Calendar\nДата: {day:%d.%m.%Y}\nДобавил(а): {author.name}\n\n"
    # Use a conservative bound that also fits Telegram's UTF-16 accounting.
    clipped = body if len(body) <= 1500 else body[:1499] + "…"
    footer = f"\n\n{settings.telegram_calendar_url}" if settings.telegram_calendar_url else ""
    recipients = await session.scalars(
        select(TelegramLink.user_id)
        .where(TelegramLink.user_id != author.id)
        .order_by(TelegramLink.user_id)
        .with_for_update(read=True, key_share=True)
    )
    now = datetime.now(timezone.utc)
    session.add_all(
        TelegramDelivery(recipient_id=recipient, message=header + clipped + footer, next_attempt_at=now)
        for recipient in recipients
    )


async def deliver_one(session, send) -> bool:
    now = datetime.now(timezone.utc)
    statement = (
        select(TelegramDelivery.id, TelegramLink.chat_id)
        .join(TelegramLink, TelegramDelivery.recipient_id == TelegramLink.user_id)
        .where(TelegramDelivery.next_attempt_at <= now)
        .order_by(TelegramDelivery.next_attempt_at, TelegramDelivery.id)
        .limit(1)
        .with_for_update(of=TelegramLink, key_share=True, skip_locked=True)
    )
    row = (await session.execute(statement)).first()
    if row is None:
        return False
    delivery_id, chat_id = row
    # Recheck after locking the link in case another worker committed after
    # the initial SELECT snapshot, but before this worker obtained the lock.
    delivery = await session.scalar(
        select(TelegramDelivery).where(
            TelegramDelivery.id == delivery_id,
            TelegramDelivery.next_attempt_at <= now,
        )
    )
    if delivery is None:
        return False
    try:
        await send(chat_id, delivery.message)
    except TelegramError as error:
        if error.status in (400, 403):
            log.warning("Telegram rejected delivery %s (code %s)", delivery.id, error.status)
            await session.delete(delivery)
        else:
            delivery.attempts += 1
            delay = max(min(3600, 5 * 2 ** min(delivery.attempts - 1, 10)), min(86400, error.retry_after))
            delivery.next_attempt_at = datetime.now(timezone.utc) + timedelta(seconds=delay)
            log.warning("Telegram delivery %s will retry (code %s)", delivery.id, error.status)
    else:
        await session.delete(delivery)
    await session.commit()
    return True


async def run_delivery_worker():
    settings = get_settings()

    async def send(chat_id, message):
        await asyncio.to_thread(
            bot_request,
            settings.telegram_bot_token.get_secret_value(),
            settings.telegram_proxy_url.get_secret_value(),
            "sendMessage",
            {"chat_id": chat_id, "text": message, "link_preview_options": {"is_disabled": True}},
        )

    while True:
        try:
            async with SessionLocal() as session:
                if await deliver_one(session, send):
                    continue
        except Exception as error:
            # Avoid logging request URLs, credentials, message text or database values.
            log.error("Telegram delivery worker error (%s)", type(error).__name__)
        await asyncio.sleep(1)
