"""Manage Telegram opt-ins from the backend container."""
import argparse
import asyncio

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.config import get_settings
from app.database import SessionLocal
from app.models import TelegramLink, User
from app.services.telegram import TelegramError, bot_request


async def run(args):
    settings = get_settings()
    token = settings.telegram_bot_token.get_secret_value()
    proxy = settings.telegram_proxy_url.get_secret_value()
    async with SessionLocal() as session:
        user_id = await session.scalar(select(User.id).where(User.login == args.login.strip().casefold()))
        if user_id is None:
            raise SystemExit("Пользователь календаря не найден.")
        link = await session.get(TelegramLink, user_id)
        if args.action == "unlink":
            if link is not None:
                await session.delete(link)
                await session.commit()
            print("Уведомления отключены.")
            return
        if link is not None:
            if link.chat_id == args.chat_id:
                print("Этот чат уже привязан.")
                return
            raise SystemExit("Сначала отвяжите прежний чат.")
        if args.chat_id <= 0 or args.chat_id >= 2**52:
            raise SystemExit("Укажите положительный ID личного чата Telegram.")
        if not token:
            raise SystemExit("Токен бота не настроен.")
        try:
            chat = await asyncio.to_thread(bot_request, token, proxy, "getChat", {"chat_id": args.chat_id})
            if not isinstance(chat, dict) or chat.get("type") != "private" or chat.get("id") != args.chat_id:
                raise SystemExit("Бот не подтвердил личный чат.")
        except TelegramError as error:
            raise SystemExit(f"Не удалось проверить чат в Telegram (код: {error.status or 'сеть'}).") from None
        session.add(TelegramLink(user_id=user_id, chat_id=args.chat_id))
        try:
            await session.commit()
        except IntegrityError:
            raise SystemExit("Этот чат или пользователь уже привязан.") from None
        print("Уведомления включены.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    link = commands.add_parser("link", help="Link a verified personal Telegram chat")
    link.add_argument("login")
    link.add_argument("chat_id", type=int)
    link.add_argument("--confirmed-owner", action="store_true", required=True,
                      help="Confirm that the chat belongs to the calendar user and they opted in")
    unlink = commands.add_parser("unlink")
    unlink.add_argument("login")
    asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    main()
