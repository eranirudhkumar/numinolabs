from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import loan as crud
from app.database import get_db
from app.schemas.loan import BorrowRequest, LoanListResponse, LoanResponse, PaginatedLoansResponse

router = APIRouter(prefix="/loans", tags=["Loans"])


@router.post(
    "/borrow",
    response_model=LoanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a member borrowing a book",
)
async def borrow_book(
    data: BorrowRequest,
    db: AsyncSession = Depends(get_db),
) -> LoanResponse:
    loan = await crud.borrow_book(db, data)
    return LoanResponse.model_validate(loan)


@router.post(
    "/{loan_id}/return",
    response_model=LoanResponse,
    summary="Return a borrowed book",
)
async def return_book(
    loan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> LoanResponse:
    loan = await crud.return_book(db, loan_id)
    return LoanResponse.model_validate(loan)


@router.get(
    "/overdue",
    response_model=LoanListResponse,
    summary="List all overdue loans",
)
async def list_overdue_loans(
    db: AsyncSession = Depends(get_db),
) -> LoanListResponse:
    loans = await crud.list_overdue_loans(db)
    return LoanListResponse(
        loans=[LoanResponse.model_validate(loan) for loan in loans],
        total=len(loans),
    )


@router.get(
    "/member/{member_id}",
    response_model=LoanListResponse,
    summary="Get all loans for a specific member",
)
async def list_loans_by_member(
    member_id: uuid.UUID,
    active_only: bool = Query(
        False,
        description="If true, return only active and overdue loans (excludes returned)",
    ),
    db: AsyncSession = Depends(get_db),
) -> LoanListResponse:
    loans = await crud.list_loans_by_member(db, member_id, active_only)
    return LoanListResponse(
        loans=[LoanResponse.model_validate(loan) for loan in loans],
        total=len(loans),
    )


@router.get(
    "/",
    response_model=PaginatedLoansResponse,
    summary="List all loans (paginated)",
)
async def list_all_loans(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedLoansResponse:
    loans, total = await crud.list_all_loans(db, page, page_size)
    return PaginatedLoansResponse(
        loans=[LoanResponse.model_validate(loan) for loan in loans],
        total=total,
        page=page,
        page_size=page_size,
    )
