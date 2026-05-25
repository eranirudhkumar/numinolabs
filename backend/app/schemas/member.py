from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.models.member import MembershipStatus


class MemberBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100, examples=["Alice"])
    last_name: str = Field(..., min_length=1, max_length=100, examples=["Smith"])
    email: EmailStr = Field(..., examples=["alice@example.com"])
    phone: Optional[str] = Field(None, max_length=20, examples=["+1-555-0100"])
    address: Optional[str] = Field(None, examples=["123 Main St, Springfield"])

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def strip_names(cls, v: object) -> object:
        return v.strip() if isinstance(v, str) else v

    @field_validator("phone", "address", mode="before")
    @classmethod
    def strip_optional_contact(cls, v: object) -> object:
        if isinstance(v, str):
            stripped = v.strip()
            # Treat an empty / whitespace-only string as "not provided"
            return stripped if stripped else None
        return v


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    membership_status: Optional[MembershipStatus] = None

    @model_validator(mode="before")
    @classmethod
    def required_fields_cannot_be_null(cls, data: object) -> object:
        """Reject explicit null for columns that are NOT NULL in the database.

        A PATCH request should omit a field to leave it unchanged; sending
        null for a required field is a client error, not a "clear" operation.
        """
        if isinstance(data, dict):
            for field in ("first_name", "last_name", "email", "membership_status"):
                if field in data and data[field] is None:
                    raise ValueError(
                        f"'{field}' is required and cannot be set to null. "
                        "Omit the field to leave it unchanged."
                    )
        return data

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def strip_names(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if v else v

    @field_validator("phone", "address", mode="before")
    @classmethod
    def strip_optional_contact(cls, v: object) -> object:
        if isinstance(v, str):
            stripped = v.strip()
            return stripped if stripped else None
        return v


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
