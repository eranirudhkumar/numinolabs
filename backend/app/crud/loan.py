from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.config import settings
from app.crud.member import get_member
from app.models.book import Book
from app.models.loan import Loan, LoanStatus
from app.models.member import MembershipStatus
from app.schemas.loan import BorrowRequest


async def borrow_book(db: AsyncSession, data: BorrowRequest) -> Loan:
    member = await get_member(db, data.member_id)
    if member.membership_status != MembershipStatus.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Member '{member.email}' cannot borrow books — "
                f"membership status is '{member.membership_status.value}'."
            ),
        )

    book = await db.scalar(
        select(Book).where(Book.id == data.book_id).with_for_update()
    )
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id '{data.book_id}' not found.",
        )
    if book.available_copies < 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"'{book.title}' has no available copies at the moment.",
        )

    now = datetime.now(tz=timezone.utc)
    loan = Loan(
        book_id=book.id,
        member_id=member.id,
        borrowed_at=now,
        due_date=now + timedelta(days=settings.loan_period_days),
        status=LoanStatus.active,
        fine_amount=Decimal("0.00"),
    )
    db.add(loan)
    book.available_copies -= 1

    await db.flush()

    result = await db.scalar(
        select(Loan)
        .where(Loan.id == loan.id)
        .options(joinedload(Loan.book), joinedload(Loan.member))
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Loan record not found after creation.",
        )
    return result


async def return_book(db: AsyncSession, loan_id: uuid.UUID) -> Loan:
    loan = await db.scalar(
        select(Loan)
        .where(Loan.id == loan_id)
        .options(joinedload(Loan.book), joinedload(Loan.member))
        .with_for_update()
    )
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Loan with id '{loan_id}' not found.",
        )

    if loan.status == LoanStatus.returned:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Loan '{loan_id}' has already been returned.",
        )

    await db.scalar(select(Book).where(Book.id == loan.book_id).with_for_update())

    now = datetime.now(tz=timezone.utc)
    loan.returned_at = now
    loan.status = LoanStatus.returned

    if now > loan.due_date:
        days_late = (now - loan.due_date).days or 1
        loan.fine_amount = round(Decimal(str(settings.fine_per_day)) * days_late, 2)

    loan.book.available_copies += 1

    await db.flush()
    await db.refresh(loan, attribute_names=["returned_at", "fine_amount", "status", "updated_at"])
    await db.refresh(loan.book, attribute_names=["available_copies", "updated_at"])
    return loan


async def list_loans_by_member(
    db: AsyncSession,
    member_id: uuid.UUID,
    active_only: bool = False,
) -> list[Loan]:
    await get_member(db, member_id)

    query = (
        select(Loan)
        .where(Loan.member_id == member_id)
        .options(joinedload(Loan.book), joinedload(Loan.member))
        .order_by(Loan.borrowed_at.desc(), Loan.id)
    )
    if active_only:
        query = query.where(Loan.status.in_([LoanStatus.active, LoanStatus.overdue]))

    result = await db.scalars(query)
    return list(result.unique())


async def list_overdue_loans(db: AsyncSession) -> list[Loan]:
    now = datetime.now(tz=timezone.utc)
    loans = (
        await db.scalars(
            select(Loan)
            .where(
                Loan.due_date < now,
                Loan.status.in_([LoanStatus.active, LoanStatus.overdue]),
            )
            .options(joinedload(Loan.book), joinedload(Loan.member))
            .order_by(Loan.due_date, Loan.id)
        )
    ).unique().all()

    to_transition = [loan for loan in loans if loan.status == LoanStatus.active]
    for loan in to_transition:
        loan.status = LoanStatus.overdue

    if to_transition:
        await db.flush()
        for loan in to_transition:
            await db.refresh(loan, attribute_names=["status", "updated_at"])

    return list(loans)


async def list_all_loans(
    db: AsyncSession, page: int = 1, page_size: int = 20
) -> tuple[list[Loan], int]:
    query = (
        select(Loan)
        .options(joinedload(Loan.book), joinedload(Loan.member))
        .order_by(Loan.borrowed_at.desc(), Loan.id)
    )
    total = await db.scalar(select(func.count(Loan.id)).select_from(Loan))
    loans = (
        await db.scalars(query.offset((page - 1) * page_size).limit(page_size))
    ).unique().all()
    return list(loans), total or 0
