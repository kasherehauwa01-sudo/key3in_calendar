import calendar
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Note

async def by_date(session: AsyncSession, note_date: date) -> Note | None:
    return await session.scalar(select(Note).where(Note.date == note_date))

async def month(session: AsyncSession, year: int, month_number: int) -> list[Note]:
    last = calendar.monthrange(year, month_number)[1]
    result = await session.scalars(select(Note).where(Note.date.between(date(year, month_number, 1), date(year, month_number, last))).order_by(Note.date))
    return list(result)

async def search(session: AsyncSession, query: str) -> list[Note]:
    escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    result = await session.scalars(select(Note).where(Note.text.ilike(f"%{escaped}%", escape="\\")).order_by(Note.date))
    return list(result)
