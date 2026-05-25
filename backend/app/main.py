from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import settings
from app.database import AsyncSessionLocal, engine
from app.models import book, loan, member  # noqa: F401
from app.routers import books, loans, members


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="Neighborhood Library Service",
    description=(
        "REST API for managing library books, members, and lending operations. "
        "Service contract defined in `proto/library.proto`."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"

app.include_router(books.router, prefix=API_PREFIX)
app.include_router(members.router, prefix=API_PREFIX)
app.include_router(loans.router, prefix=API_PREFIX)


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ok", "service": "neighborhood-library", "database": "ok"}
    except Exception:
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "service": "neighborhood-library",
                "database": "unreachable",
            },
        )
