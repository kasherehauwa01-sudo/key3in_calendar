from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.models import Note, NotificationRead, User
from app.schemas.notification import NotificationRead as NotificationReadSchema
from app.services.auth import current_user

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationReadSchema])
async def notifications(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
):
    """Возвращает заметки других пользователей и состояние их прочтения."""
    was_read = exists().where(
        NotificationRead.user_id == user.id,
        NotificationRead.note_id == Note.id,
    )
    rows = await session.execute(
        select(Note, was_read.label("is_read"))
        .options(selectinload(Note.user))
        .where(Note.user_id != user.id)
        .order_by(Note.created_at.desc(), Note.id.desc())
    )
    return [
        NotificationReadSchema(
            note_id=note.id,
            date=note.date,
            user_id=note.user_id,
            user_name=note.user.name,
            user_color=note.user.color,
            text=note.text,
            created_at=note.created_at,
            is_read=is_read,
        )
        for note, is_read in rows
    ]


@router.put("/{note_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def read_notification(
    note_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
):
    note = await session.get(Note, note_id)
    if note and note.user_id != user.id:
        await session.merge(NotificationRead(user_id=user.id, note_id=note_id))
        await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def read_all_notifications(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
):
    note_ids = await session.scalars(select(Note.id).where(Note.user_id != user.id))
    for note_id in note_ids:
        await session.merge(NotificationRead(user_id=user.id, note_id=note_id))
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
