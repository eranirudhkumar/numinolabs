from __future__ import annotations

import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import TIMESTAMP, CheckConstraint, Enum, ForeignKey, Index, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.member import Member


class LoanStatus(str, enum.Enum):
    active = "active"
    returned = "returned"
    overdue = "overdue"


class Loan(Base, TimestampMixin):
    """One row represents a single borrow/return transaction."""

    __tablename__ = "loans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("books.id", ondelete="RESTRICT"),
        nullable=False,
    )
    member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("members.id", ondelete="RESTRICT"),
        nullable=False,
    )
    borrowed_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    due_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )
    returned_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    status: Mapped[LoanStatus] = mapped_column(
        Enum(LoanStatus, name="loan_status"),
        nullable=False,
        default=LoanStatus.active,
    )
    fine_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00")
    )

    book: Mapped[Book] = relationship(
        "Book", back_populates="loans", lazy="raise_on_sql"
    )
    member: Mapped[Member] = relationship(
        "Member", back_populates="loans", lazy="raise_on_sql"
    )

    __table_args__ = (
        CheckConstraint("fine_amount >= 0", name="chk_fine_non_negative"),
        Index("idx_loans_book_id", "book_id"),
        Index("idx_loans_member_id", "member_id"),
        Index("idx_loans_status", "status"),
    )

    def __repr__(self) -> str:
        return (
            f"<Loan id={self.id} book_id={self.book_id} "
            f"member_id={self.member_id} status={self.status}>"
        )
