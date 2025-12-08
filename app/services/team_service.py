from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.team import Team

from app.schemas.team import TeamCreate, TeamUpdate
from app.utils.filtering import filter_and_paginate


async def get_teams_filtered(db: AsyncSession, params: dict):
    return await filter_and_paginate(Team, db, params)

async def get_team(db: AsyncSession, team_id: int):
    result = await db.execute(select(Team).where(Team.id == team_id))
    return result.scalar_one_or_none()

async def create_team(db: AsyncSession, data: TeamCreate):
    new_team = Team(**data.model_dump())
    db.add(new_team)
    await db.commit()
    await db.refresh(new_team)
    return  new_team

async def update_team(db: AsyncSession, team_id: int, data: TeamUpdate):
    team = await get_team(db, team_id)
    if not team:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(team, key, value)
    await db.commit()
    await db.refresh(team)
    return team

async def delete_team(db: AsyncSession, team_id: int):
    team = await get_team(db, team_id)
    if not team:
        return None
    await db.delete(team)
    await db.commit()
    return team