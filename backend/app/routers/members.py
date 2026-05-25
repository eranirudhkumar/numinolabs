from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import member as crud
from app.database import get_db
from app.schemas.member import (
    MemberCreate,
    MemberResponse,
    MemberUpdate,
    PaginatedMembersResponse,
)

router = APIRouter(prefix="/members", tags=["Members"])


@router.post(
    "/",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new library member",
)
async def create_member(
    data: MemberCreate,
    db: AsyncSession = Depends(get_db),
) -> MemberResponse:
    member = await crud.create_member(db, data)
    return MemberResponse.model_validate(member)


@router.get(
    "/",
    response_model=PaginatedMembersResponse,
    summary="List all members",
)
async def list_members(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by first name, last name, or email (partial match)"),
    db: AsyncSession = Depends(get_db),
) -> PaginatedMembersResponse:
    members, total = await crud.list_members(db, page, page_size, search)
    return PaginatedMembersResponse(
        members=[MemberResponse.model_validate(m) for m in members],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Get a single member by ID",
)
async def get_member(
    member_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> MemberResponse:
    member = await crud.get_member(db, member_id)
    return MemberResponse.model_validate(member)


@router.patch(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Partially update a member record",
)
async def update_member(
    member_id: uuid.UUID,
    data: MemberUpdate,
    db: AsyncSession = Depends(get_db),
) -> MemberResponse:
    member = await crud.update_member(db, member_id, data)
    return MemberResponse.model_validate(member)
