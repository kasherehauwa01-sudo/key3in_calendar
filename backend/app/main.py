import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import get_settings
from .routers import auth_router, notes_router

settings = get_settings()
app = FastAPI(title="Key3in API", root_path=settings.base_path, docs_url="/api/docs", openapi_url="/api/openapi.json")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth_router)
app.include_router(notes_router)

@app.get("/api/health", tags=["system"])
async def health(): return {"status": "ok"}

@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception):
    logging.exception("Необработанная ошибка %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Внутренняя ошибка сервера"})
