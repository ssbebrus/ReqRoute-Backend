from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.team_membership import TeamMembership

from app.schemas.team_membership import TeamMembershipCreate, TeamMembershipUpdate
from app.utils.filtering import filter_and_paginate


async def get_memberships_filtered(db: AsyncSession, params: dict):
    return await filter_and_paginate(TeamMembership, db, params)

async def get_membership(db: AsyncSession, membership_id: int):
    result = await db.execute(select(TeamMembership).where(TeamMembership.id == membership_id))
    return result.scalar_one_or_none()

async def create_membership(db: AsyncSession, data: TeamMembershipCreate):
    new_membership = TeamMembership(**data.model_dump())
    db.add(new_membership)
    await db.commit()
    await db.refresh(new_membership)
    return  new_membership

async def update_membership(db: AsyncSession, membership_id: int, data: TeamMembershipUpdate):
    membership = await get_membership(db, membership_id)
    if not membership:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(membership, key, value)
    await db.commit()
    await db.refresh(membership)
    return membership

async def delete_membership(db: AsyncSession, membership_id: int):
    membership = await get_membership(db, membership_id)
    if not membership:
        return None
    await db.delete(membership)
    await db.commit()
    return membership