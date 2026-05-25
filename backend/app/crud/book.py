from __future__ import annotations

import uuid
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate


async def create_book(db: AsyncSession, data: BookCreate) -> Book:
    if data.isbn:
        existing = await db.scalar(select(Book).where(Book.isbn == data.isbn))
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A book with ISBN '{data.isbn}' already exists.",
            )

    book = Book(
        isbn=data.isbn,
        title=data.title,
        author=data.author,
        genre=data.genre,
        published_year=data.published_year,
        total_copies=data.total_copies,
        available_copies=data.total_copies,
    )
    db.add(book)
    try:
        await db.flush()
        await db.refresh(book)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A book with ISBN '{data.isbn}' already exists.",
        )
    return book


async def get_book(db: AsyncSession, book_id: uuid.UUID) -> Book:
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id '{book_id}' not found.",
        )
    return book


async def list_books(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    title: Optional[str] = None,
    author: Optional[str] = None,
    genre: Optional[str] = None,
) -> tuple[list[Book], int]:
    query = select(Book)

    if title:
        query = query.where(Book.title.ilike(f"%{title}%"))
    if author:
        query = query.where(Book.author.ilike(f"%{author}%"))
    if genre:
        query = query.where(Book.genre.ilike(f"%{genre}%"))

    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    books = (
        await db.scalars(
            query.order_by(Book.title, Book.id).offset((page - 1) * page_size).limit(page_size)
        )
    ).all()
    return list(books), total or 0


async def update_book(
    db: AsyncSession, book_id: uuid.UUID, data: BookUpdate
) -> Book:
    book = await get_book(db, book_id)
    update_data = data.model_dump(exclude_unset=True)

    # Reject an ISBN update that collides with a *different* book
    if "isbn" in update_data and update_data["isbn"] is not None:
        conflict = await db.scalar(
            select(Book).where(
                Book.isbn == update_data["isbn"],
                Book.id != book_id,
            )
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"ISBN '{update_data['isbn']}' is already assigned to another book.",
            )

    if "total_copies" in update_data:
        new_total = update_data.pop("total_copies")
        if new_total is not None:
            diff = new_total - book.total_copies
            new_available = book.available_copies + diff
            if new_available < 0:
                on_loan = book.total_copies - book.available_copies
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=(
                        f"Cannot reduce total_copies to {new_total} because "
                        f"{on_loan} {'copy is' if on_loan == 1 else 'copies are'} currently on loan."
                    ),
                )
            book.total_copies = new_total
            book.available_copies = new_available

    for field, value in update_data.items():
        setattr(book, field, value)

    try:
        await db.flush()
        await db.refresh(book)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The provided ISBN is already assigned to another book.",
        )
    return book
