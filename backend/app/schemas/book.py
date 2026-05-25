from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class BookBase(BaseModel):
    isbn: Optional[str] = Field(None, max_length=20, examples=["978-0-06-112008-4"])
    title: str = Field(..., min_length=1, max_length=255, examples=["To Kill a Mockingbird"])
    author: str = Field(..., min_length=1, max_length=255, examples=["Harper Lee"])
    genre: Optional[str] = Field(None, max_length=100, examples=["Fiction"])
    published_year: Optional[int] = Field(None, ge=1000, le=2100, examples=[1960])
    total_copies: int = Field(1, ge=1, examples=[3])

    @field_validator("title", "author", mode="before")
    @classmethod
    def strip_required_str(cls, v: object) -> object:
        return v.strip() if isinstance(v, str) else v

    @field_validator("isbn", "genre", mode="before")
    @classmethod
    def strip_optional_str(cls, v: object) -> object:
        if isinstance(v, str):
            stripped = v.strip()
            # Treat an empty / whitespace-only string as "not provided"
            return stripped if stripped else None
        return v


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    isbn: Optional[str] = Field(None, max_length=20)
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    genre: Optional[str] = Field(None, max_length=100)
    published_year: Optional[int] = Field(None, ge=1000, le=2100)
    total_copies: Optional[int] = Field(None, ge=1)

    @model_validator(mode="before")
    @classmethod
    def required_fields_cannot_be_null(cls, data: object) -> object:
        """Reject explicit null for columns that are NOT NULL in the database.

        A PATCH request should omit a field to leave it unchanged; sending
        null for a required field is a client error, not a "clear" operation.
        """
        if isinstance(data, dict):
            for field in ("title", "author", "total_copies"):
                if field in data and data[field] is None:
                    raise ValueError(
                        f"'{field}' is required and cannot be set to null. "
                        "Omit the field to leave it unchanged."
                    )
        return data

    @field_validator("title", "author", mode="before")
    @classmethod
    def strip_str(cls, v: object) -> object:
        return v.strip() if isinstance(v, str) else v

    @field_validator("isbn", "genre", mode="before")
    @classmethod
    def strip_optional_str(cls, v: object) -> object:
        if isinstance(v, str):
            stripped = v.strip()
            return stripped if stripped else None
        return v


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
