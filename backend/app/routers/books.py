from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import book as crud
from app.database import get_db
from app.schemas.book import (
    BookCreate,
    BookResponse,
    BookUpdate,
    PaginatedBooksResponse,
)

router = APIRouter(prefix="/books", tags=["Books"])


@router.post(
    "/",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new book record",
)
async def create_book(
    data: BookCreate,
    db: AsyncSession = Depends(get_db),
) -> BookResponse:
    book = await crud.create_book(db, data)
    return BookResponse.model_validate(book)


@router.get(
    "/",
    response_model=PaginatedBooksResponse,
    summary="List books with optional filters",
)
async def list_books(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    title: Optional[str] = Query(None, description="Filter by title (partial match)"),
    author: Optional[str] = Query(None, description="Filter by author name (partial match)"),
    genre: Optional[str] = Query(None, description="Filter by genre (partial match)"),
    db: AsyncSession = Depends(get_db),
) -> PaginatedBooksResponse:
    books, total = await crud.list_books(db, page, page_size, title, author, genre)
    return PaginatedBooksResponse(
        books=[BookResponse.model_validate(b) for b in books],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{book_id}",
    response_model=BookResponse,
    summary="Get a single book by ID",
)
async def get_book(
    book_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> BookResponse:
    book = await crud.get_book(db, book_id)
    return BookResponse.model_validate(book)


@router.patch(
    "/{book_id}",
    response_model=BookResponse,
    summary="Partially update a book record",
)
async def update_book(
    book_id: uuid.UUID,
    data: BookUpdate,
    db: AsyncSession = Depends(get_db),
) -> BookResponse:
    book = await crud.update_book(db, book_id, data)
    return BookResponse.model_validate(book)
