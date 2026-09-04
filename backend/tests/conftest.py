import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.database import get_session
from app.main import app
from app.models import Base

engine = create_async_engine(os.environ["DATABASE_URL"])
Session = async_sessionmaker(engine, expire_on_commit=False)
async def test_session():
    async with Session() as session: yield session
app.dependency_overrides[get_session] = test_session

@pytest_asyncio.fixture(autouse=True)
async def database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all); await conn.run_sync(Base.metadata.create_all)
    yield

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as value: yield value
