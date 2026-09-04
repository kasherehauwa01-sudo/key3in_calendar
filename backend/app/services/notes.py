import calendar
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models import Note

LOAD_USER = selectinload(Note.user)

async def by_date_and_user(session: AsyncSession, note_date: date, user_id: int) -> Note | None:
    return await session.scalar(select(Note).options(LOAD_USER).where(Note.date == note_date, Note.user_id == user_id))

async def month(session: AsyncSession, year: int, month_number: int) -> list[Note]:
    last = calendar.monthrange(year, month_number)[1]
    result = await session.scalars(select(Note).options(LOAD_USER).where(Note.date.between(date(year, month_number, 1), date(year, month_number, last))).order_by(Note.date, Note.id))
    return list(result)

async def search(session: AsyncSession, query: str) -> list[Note]:
    escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    result = await session.scalars(select(Note).options(LOAD_USER).where(Note.text.ilike(f"%{escaped}%", escape="\\")).order_by(Note.date, Note.id))
    return list(result)
