from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.loan import LoanStatus
from app.schemas.book import BookResponse
from app.schemas.member import MemberResponse


class BorrowRequest(BaseModel):
    book_id: uuid.UUID
    member_id: uuid.UUID


class LoanResponse(BaseModel):
    id: uuid.UUID
    book_id: uuid.UUID
    member_id: uuid.UUID
    book: BookResponse
    member: MemberResponse
    status: LoanStatus
    fine_amount: float
    borrowed_at: datetime
    due_date: datetime
    returned_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LoanListResponse(BaseModel):
    loans: list[LoanResponse]
    total: int
