from datetime import datetime, timezone

import pytest
from pydantic import SecretStr
from sqlalchemy import select

from app.config import get_settings
from app.models import TelegramDelivery, TelegramLink
from app.services.telegram import TelegramError, deliver_one
from conftest import Session

pytestmark = pytest.mark.asyncio


async def register(client, name):
    response = await client.post("/api/auth/register", json={"login": name, "pin": "1234", "name": name})
    assert response.status_code == 201
    data = response.json()
    return data["user"]["id"], {"Authorization": f"Bearer {data['token']}"}


async def test_only_new_events_queue_for_other_opted_in_users(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "telegram_bot_token", SecretStr("1:test"))
    author, headers = await register(client, "anna")
    other, _ = await register(client, "boris")
    await register(client, "clara")
    async with Session() as session:
        session.add_all([TelegramLink(user_id=author, chat_id=1), TelegramLink(user_id=other, chat_id=2)])
        await session.commit()

    assert (await client.post("/api/notes", headers=headers, json={"date": "2026-12-01", "text": "Обычное"})).status_code == 201
    assert (await client.post("/api/notes", headers=headers, json={"date": "2026-12-01", "text": "Дубликат"})).status_code == 409
    assert (await client.put("/api/notes/2026-12-01", headers=headers, json={"text": "Правка"})).status_code == 200
    assert (await client.put("/api/notes/2026-12-02", headers=headers, json={"text": "Новая запись"})).status_code == 200
    assert (await client.post("/api/recurring-events", headers=headers, json={
        "text": "Планёрка", "start_date": "2026-12-03", "interval": 1, "unit": "week",
    })).status_code == 201
    async with Session() as session:
        rows = (await session.scalars(select(TelegramDelivery).order_by(TelegramDelivery.id))).all()
        assert [row.recipient_id for row in rows] == [other] * 3
        assert all(text in row.message for text, row in zip(["Обычное", "Новая запись", "Планёрка"], rows))

    monkeypatch.setattr(get_settings(), "telegram_bot_token", SecretStr(""))
    assert (await client.put("/api/notes/2026-12-04", headers=headers, json={"text": "Бот выключен"})).status_code == 200
    async with Session() as session:
        assert len((await session.scalars(select(TelegramDelivery))).all()) == 3


async def test_delivery_retries_and_removes_sent_item(client):
    user_id, _ = await register(client, "anna")
    async with Session() as session:
        session.add(TelegramLink(user_id=user_id, chat_id=123))
        await session.flush()
        session.add(TelegramDelivery(recipient_id=user_id, message="Тест", next_attempt_at=datetime.now(timezone.utc)))
        await session.commit()

    async def unavailable(chat_id, message):
        raise TelegramError(429, retry_after=30)

    async with Session() as session:
        assert await deliver_one(session, unavailable)
        pending = await session.scalar(select(TelegramDelivery))
        assert pending.attempts == 1
        assert (pending.next_attempt_at.replace(tzinfo=timezone.utc) - datetime.now(timezone.utc)).total_seconds() > 25
        assert not await deliver_one(session, unavailable)
        pending.next_attempt_at = datetime.now(timezone.utc)
        await session.commit()

    sent = []

    async def send(chat_id, message):
        sent.append((chat_id, message))

    async with Session() as session:
        assert await deliver_one(session, send)
        assert not await deliver_one(session, send)
    assert sent == [(123, "Тест")]
