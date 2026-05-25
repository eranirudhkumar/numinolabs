from __future__ import annotations

import enum
import uuid
from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, Enum, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.loan import Loan


class MembershipStatus(str, enum.Enum):
    active = "active"
    suspended = "suspended"
    expired = "expired"


class Member(Base, TimestampMixin):
    """A registered library member / cardholder."""

    __tablename__ = "members"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    membership_status: Mapped[MembershipStatus] = mapped_column(
        Enum(MembershipStatus, name="membership_status"),
        nullable=False,
        default=MembershipStatus.active,
    )
    membership_date: Mapped[date] = mapped_column(
        Date, nullable=False, default=date.today
    )

    loans: Mapped[list[Loan]] = relationship(
        "Loan", back_populates="member", lazy="select"
    )

    __table_args__ = (
        Index("idx_members_email", "email"),
        Index("idx_members_last_name", "last_name"),
    )

    def __repr__(self) -> str:
        return f"<Member id={self.id} email={self.email!r}>"
