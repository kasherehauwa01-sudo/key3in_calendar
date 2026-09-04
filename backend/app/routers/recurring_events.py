from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database import get_session
from app.models import RecurringEvent, User
from app.schemas import RecurringEventRead, RecurringEventWrite
from app.services.auth import current_user

router=APIRouter(prefix="/api/recurring-events",tags=["recurring-events"])

@router.get("",response_model=list[RecurringEventRead])
async def list_events(session:AsyncSession=Depends(get_session),_:User=Depends(current_user)):
    return list(await session.scalars(select(RecurringEvent).options(selectinload(RecurringEvent.user)).order_by(RecurringEvent.id)))

@router.post("",response_model=RecurringEventRead,status_code=201)
async def create_event(payload:RecurringEventWrite,session:AsyncSession=Depends(get_session),user:User=Depends(current_user)):
    event=RecurringEvent(**payload.model_dump(),user_id=user.id,user=user);session.add(event);await session.commit();await session.refresh(event);return event

@router.put("/{event_id}",response_model=RecurringEventRead)
async def update_event(event_id:int,payload:RecurringEventWrite,session:AsyncSession=Depends(get_session),user:User=Depends(current_user)):
    event=await session.scalar(select(RecurringEvent).options(selectinload(RecurringEvent.user)).where(RecurringEvent.id==event_id,RecurringEvent.user_id==user.id))
    if not event: raise HTTPException(404,"Событие не найдено")
    for key,value in payload.model_dump().items(): setattr(event,key,value)
    await session.commit();await session.refresh(event);return event

@router.delete("/{event_id}",status_code=204)
async def delete_event(event_id:int,response:Response,session:AsyncSession=Depends(get_session),user:User=Depends(current_user)):
    event=await session.scalar(select(RecurringEvent).where(RecurringEvent.id==event_id,RecurringEvent.user_id==user.id))
    if event: await session.delete(event);await session.commit()
    return response
