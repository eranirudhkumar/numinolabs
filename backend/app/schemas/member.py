from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.member import MembershipStatus


class MemberBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100, examples=["Alice"])
    last_name: str = Field(..., min_length=1, max_length=100, examples=["Smith"])
    email: EmailStr = Field(..., examples=["alice@example.com"])
    phone: Optional[str] = Field(None, max_length=20, examples=["+1-555-0100"])
    address: Optional[str] = Field(None, examples=["123 Main St, Springfield"])

    @field_validator("first_name", "last_name")
    @classmethod
    def strip_names(cls, v: str) -> str:
        return v.strip()


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    membership_status: Optional[MembershipStatus] = None

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def strip_names(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if v else v


class MemberResponse(MemberBase):
    id: uuid.UUID
    membership_status: MembershipStatus
    membership_date: date
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedMembersResponse(BaseModel):
    members: list[MemberResponse]
    total: int
    page: int
    page_size: int
