from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class BookBase(BaseModel):
    isbn: Optional[str] = Field(None, max_length=20, examples=["978-0-06-112008-4"])
    title: str = Field(..., min_length=1, max_length=255, examples=["To Kill a Mockingbird"])
    author: str = Field(..., min_length=1, max_length=255, examples=["Harper Lee"])
    genre: Optional[str] = Field(None, max_length=100, examples=["Fiction"])
    published_year: Optional[int] = Field(None, ge=1000, le=2100, examples=[1960])
    total_copies: int = Field(1, ge=1, examples=[3])

    @field_validator("title", "author")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    isbn: Optional[str] = Field(None, max_length=20)
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    genre: Optional[str] = Field(None, max_length=100)
    published_year: Optional[int] = Field(None, ge=1000, le=2100)
    total_copies: Optional[int] = Field(None, ge=1)

    @field_validator("title", "author", mode="before")
    @classmethod
    def strip_if_present(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if v else v


class BookResponse(BookBase):
    id: uuid.UUID
    available_copies: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedBooksResponse(BaseModel):
    books: list[BookResponse]
    total: int
    page: int
    page_size: int
