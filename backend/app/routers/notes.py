from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import Note
from app.schemas import NoteCreate, NoteRead, NoteUpdate
from app.services import notes as service

router = APIRouter(prefix="/api/notes", tags=["notes"])

def clean(text: str) -> str:
    return text.strip()

@router.get("/search", response_model=list[NoteRead])
async def search_notes(q: str = Query(min_length=1, max_length=200), session: AsyncSession = Depends(get_session)):
    return await service.search(session, q.strip()) if q.strip() else []

@router.get("", response_model=list[NoteRead])
async def get_month(year: int = Query(ge=1, le=9999), month: int = Query(ge=1, le=12), session: AsyncSession = Depends(get_session)):
    return await service.month(session, year, month)

@router.get("/{note_date}", response_model=NoteRead)
async def get_note(note_date: date, session: AsyncSession = Depends(get_session)):
    note = await service.by_date(session, note_date)
    if not note: raise HTTPException(404, "Заметка не найдена")
    return note

@router.post("", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
async def create_note(payload: NoteCreate, session: AsyncSession = Depends(get_session)):
    text = clean(payload.text)
    if not text: raise HTTPException(422, "Текст заметки не может быть пустым")
    note = Note(date=payload.date, text=text)
    session.add(note)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback(); raise HTTPException(409, "На эту дату уже есть заметка")
    await session.refresh(note)
    return note

@router.put("/{note_date}", response_model=NoteRead | None)
async def update_note(note_date: date, payload: NoteUpdate, response: Response, session: AsyncSession = Depends(get_session)):
    note = await service.by_date(session, note_date)
    if not note: raise HTTPException(404, "Заметка не найдена")
    text = clean(payload.text)
    if not text:
        await session.delete(note); await session.commit(); response.status_code = 204; return None
    note.text = text
    await session.commit(); await session.refresh(note)
    return note

@router.delete("/{note_date}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_date: date, session: AsyncSession = Depends(get_session)):
    note = await service.by_date(session, note_date)
    if not note: raise HTTPException(404, "Заметка не найдена")
    await session.delete(note); await session.commit()
