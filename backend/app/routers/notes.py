from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import Note, User
from app.schemas import NoteCreate, NoteRead, NoteUpdate
from app.services import notes as service
from app.services.auth import current_user

router = APIRouter(prefix="/api/notes", tags=["notes"])

def clean(text: str) -> str:
    return text.strip()

@router.get("/search", response_model=list[NoteRead])
async def search_notes(q: str = Query(min_length=1, max_length=200), session: AsyncSession = Depends(get_session), _: User = Depends(current_user)):
    return await service.search(session, q.strip()) if q.strip() else []

@router.get("", response_model=list[NoteRead])
async def get_month(year: int = Query(ge=1, le=9999), month: int = Query(ge=1, le=12), session: AsyncSession = Depends(get_session), _: User = Depends(current_user)):
    return await service.month(session, year, month)

@router.get("/{note_date}", response_model=list[NoteRead])
async def get_notes(note_date: date, session: AsyncSession = Depends(get_session), _: User = Depends(current_user)):
    return [note for note in await service.month(session, note_date.year, note_date.month) if note.date == note_date]

@router.post("", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
async def create_note(payload: NoteCreate, session: AsyncSession = Depends(get_session), user: User = Depends(current_user)):
    text = clean(payload.text)
    if not text: raise HTTPException(422, "Текст заметки не может быть пустым")
    note = Note(date=payload.date, text=text, user_id=user.id, user=user)
    session.add(note)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback(); raise HTTPException(409, "Вы уже оставили заметку на эту дату")
    await session.refresh(note)
    return note

@router.put("/{note_date}", response_model=NoteRead | None)
async def update_note(note_date: date, payload: NoteUpdate, response: Response, session: AsyncSession = Depends(get_session), user: User = Depends(current_user)):
    note = await service.by_date_and_user(session, note_date, user.id)
    text = clean(payload.text)
    if not text:
        if note: await session.delete(note); await session.commit()
        response.status_code = 204; return None
    if not note:
        note = Note(date=note_date, text=text, user_id=user.id, user=user); session.add(note)
    else: note.text = text
    await session.commit(); await session.refresh(note)
    return note

@router.delete("/{note_date}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_date: date, session: AsyncSession = Depends(get_session), user: User = Depends(current_user)):
    note = await service.by_date_and_user(session, note_date, user.id)
    if note: await session.delete(note); await session.commit()
