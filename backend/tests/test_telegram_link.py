from datetime import timedelta
from urllib.parse import parse_qs, urlsplit

import pytest
from pydantic import SecretStr

from app.config import get_settings
from app.models import TelegramLinkRequest
from app.services.telegram_link import link_update, now_utc, token_hash
from conftest import Session

pytestmark = pytest.mark.asyncio
PATH = "/api/users/me/telegram"


@pytest.fixture
def enable_bot(monkeypatch):
    monkeypatch.setattr(get_settings(), "telegram_bot_token", SecretStr("1:test"))
    monkeypatch.setattr(get_settings(), "telegram_bot_username", "example_bot")


async def register(client, name):
    response = await client.post("/api/auth/register", json={"login": name, "pin": "1234", "name": name})
    assert response.status_code == 201
    data = response.json()
    return data["user"]["id"], {"Authorization": f"Bearer {data['token']}"}


async def start(client, headers):
    result = await client.post(PATH + "/connect", headers=headers)
    assert result.status_code == 200
    assert result.headers["cache-control"] == "no-store"
    url = urlsplit(result.json()["url"])
    assert (url.netloc, url.path) == ("t.me", "/example_bot")
    return parse_qs(url.query)["start"][0]


async def update(token, chat_id=100, chat_type="private"):
    async with Session() as session:
        return await link_update(session, {"text": "/start " + token, "chat": {"id": chat_id, "type": chat_type}})


async def test_private_chat_links_only_its_own_calendar_account(client, enable_bot):
    assert (await client.post(PATH + "/connect")).status_code == 401
    user, anna = await register(client, "anna")
    _, boris = await register(client, "boris")
    token = await start(client, anna)
    async with Session() as session:
        assert (await session.get(TelegramLinkRequest, user)).token_hash == token_hash(token)
    assert (await client.get(PATH, headers=anna)).json() == {"available": True, "connected": False, "pending": True}
    assert await update(token, chat_type="group") is None
    assert "Telegram подключён" in (await update(token))[1]
    assert "недействительна" in (await update(token, chat_id=101))[1]
    assert (await client.get(PATH, headers=anna)).json()["connected"]
    assert not (await client.get(PATH, headers=boris)).json()["connected"]
    assert "другому аккаунту" in (await update(await start(client, boris)))[1]
    assert (await client.post(PATH + "/connect", headers=anna)).status_code == 409
    assert (await client.delete(PATH, headers=anna)).status_code == 204
    assert not (await client.get(PATH, headers=anna)).json()["connected"]


async def test_replaced_expired_and_cancelled_links_are_rejected(client, enable_bot):
    user, headers = await register(client, "anna")
    old = await start(client, headers)
    current = await start(client, headers)
    assert "недействительна" in (await update(old))[1]
    async with Session() as session:
        row = await session.get(TelegramLinkRequest, user)
        row.expires_at = now_utc() - timedelta(seconds=1)
        await session.commit()
    assert "недействительна" in (await update(current))[1]
    assert not (await client.get(PATH, headers=headers)).json()["pending"]
    current = await start(client, headers)
    assert (await client.delete(PATH, headers=headers)).status_code == 204
    assert "недействительна" in (await update(current))[1]


async def test_link_unavailable_without_config(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "telegram_bot_token", SecretStr(""))
    _, headers = await register(client, "anna")
    assert not (await client.get(PATH, headers=headers)).json()["available"]
    assert (await client.post(PATH + "/connect", headers=headers)).status_code == 503
