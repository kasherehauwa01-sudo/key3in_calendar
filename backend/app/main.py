import asyncio
import logging
from contextlib import asynccontextmanager, suppress
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import get_settings
from .routers import auth_router, notes_router, notifications_router, recurring_events_router

from .services.telegram import run_delivery_worker

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    worker = None
    if settings.telegram_bot_token.get_secret_value():
        worker = asyncio.create_task(run_delivery_worker())
    try:
        yield
    finally:
        if worker is not None:
            worker.cancel()
            with suppress(asyncio.CancelledError):
                await worker


app = FastAPI(lifespan=lifespan, title="Key3in API", root_path=settings.base_path, docs_url="/api/docs", openapi_url="/api/openapi.json")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth_router)
app.include_router(notes_router)
app.include_router(notifications_router)
app.include_router(recurring_events_router)

@app.get("/api/health", tags=["system"])
async def health(): return {"status": "ok"}

@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception):
    logging.exception("Необработанная ошибка %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Внутренняя ошибка сервера"})
