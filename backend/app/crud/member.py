from __future__ import annotations

import uuid
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.member import Member
from app.schemas.member import MemberCreate, MemberUpdate


async def create_member(db: AsyncSession, data: MemberCreate) -> Member:
    existing = await db.scalar(select(Member).where(Member.email == data.email))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A member with email '{data.email}' already exists.",
        )

    member = Member(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        phone=data.phone,
        address=data.address,
    )
    db.add(member)
    try:
        await db.flush()
        await db.refresh(member)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A member with email '{data.email}' already exists.",
        )
    return member


async def get_member(db: AsyncSession, member_id: uuid.UUID) -> Member:
    member = await db.get(Member, member_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with id '{member_id}' not found.",
        )
    return member


async def list_members(
    db: AsyncSession, page: int = 1, page_size: int = 20, search: Optional[str] = None
) -> tuple[list[Member], int]:
    query = select(Member)

    if search:
        pattern = f"%{search}%"
        query = query.where(
            or_(
                Member.first_name.ilike(pattern),
                Member.last_name.ilike(pattern),
                Member.email.ilike(pattern),
            )
        )

    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    members = (
        await db.scalars(
            query.order_by(Member.last_name, Member.first_name, Member.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    ).all()
    return list(members), total or 0


async def update_member(
    db: AsyncSession, member_id: uuid.UUID, data: MemberUpdate
) -> Member:
    member = await get_member(db, member_id)
    update_data = data.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] != member.email:
        conflict = await db.scalar(
            select(Member).where(Member.email == update_data["email"])
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{update_data['email']}' is already in use.",
            )

    for field, value in update_data.items():
        setattr(member, field, value)

    try:
        await db.flush()
        await db.refresh(member)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The provided email address is already in use by another member.",
        )
    return member
