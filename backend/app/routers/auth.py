from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import User
from app.schemas import AuthResponse, Credentials, RegisterRequest, UserRead, UserUpdate
from app.services.auth import create_session, current_user, hash_pin, verify_pin

router = APIRouter(prefix="/api", tags=["auth"])

@router.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_session)):
    login = payload.login.casefold()
    if await session.scalar(select(User).where(func.lower(User.login) == login)):
        raise HTTPException(409, "Этот логин уже занят")
    user = User(login=login, name=payload.name.strip(), pin_hash=hash_pin(payload.pin))
    session.add(user)
    await session.flush()
    token = await create_session(session, user)
    return AuthResponse(token=token, user=user)

@router.post("/auth/login", response_model=AuthResponse)
async def login(payload: Credentials, session: AsyncSession = Depends(get_session)):
    user = await session.scalar(select(User).where(func.lower(User.login) == payload.login.casefold()))
    if not user or not verify_pin(payload.pin, user.pin_hash):
        raise HTTPException(401, "Неверный логин или пин-код")
    token = await create_session(session, user)
    return AuthResponse(token=token, user=user)

@router.get("/users/me", response_model=UserRead)
async def me(user: User = Depends(current_user)):
    return user

@router.put("/users/me", response_model=UserRead)
async def update_me(payload: UserUpdate, user: User = Depends(current_user), session: AsyncSession = Depends(get_session)):
    user.name = payload.name
    user.color = payload.color.lower()
    await session.commit()
    await session.refresh(user)
    return user
