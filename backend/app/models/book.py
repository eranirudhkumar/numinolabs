from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, Index, Integer, SmallInteger, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.loan import Loan


class Book(Base, TimestampMixin):
    """Represents a book title + physical copy count the library owns."""

    __tablename__ = "books"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    isbn: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    genre: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    published_year: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    total_copies: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    available_copies: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    loans: Mapped[list[Loan]] = relationship(
        "Loan", back_populates="book", lazy="select"
    )

    __table_args__ = (
        CheckConstraint("total_copies >= 1", name="chk_total_copies_min"),
        CheckConstraint("available_copies >= 0", name="chk_available_copies_min"),
        CheckConstraint(
            "available_copies <= total_copies", name="chk_copies_max"
        ),
        Index("idx_books_isbn", "isbn"),
        Index("idx_books_author", "author"),
        Index("idx_books_title", "title"),
    )

    def __repr__(self) -> str:
        return f"<Book id={self.id} title={self.title!r}>"
