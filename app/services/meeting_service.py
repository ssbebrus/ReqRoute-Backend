from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.meeting import Meeting, MeetingUser
from app.schemas.meeting import MeetingCreate, MeetingUpdate
from app.schemas.meeting_user import MeetingUserCreate

async def get_all_meetings(db: AsyncSession):
    result = await db.execute(select(Meeting))
    return result.scalars().all()

async def get_all_meetings_on_team(db: AsyncSession, team_id: int):
    result = await db.execute(select(Meeting).where(Meeting.team_id == team_id))
    return result.scalars().all()

async def get_previous_meeting_id(db: AsyncSession, meeting_id: int):
    prev_id = await db.execute(select(Meeting.previous_meeting_id).where(Meeting.id == meeting_id))
    return prev_id.scalar_one_or_none()

async def get_meeting(db: AsyncSession, meeting_id: int):
    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    return result.scalar_one_or_none()

async def link_meeting_user(db: AsyncSession, data: MeetingUserCreate):
    new_link = MeetingUser(**data.model_dump())
    db.add(new_link)
    await db.commit()
    await db.refresh(new_link)
    return new_link

async def create_meeting(db: AsyncSession, data: MeetingCreate):
    new_meeting = Meeting(**data.model_dump())
    db.add(new_meeting)
    await db.commit()
    await db.refresh(new_meeting)
    return  new_meeting

async def update_meeting(db: AsyncSession, meeting_id: int, data: MeetingUpdate):
    meeting = await get_meeting(db, meeting_id)
    if not meeting:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(meeting, key, value)
    await db.commit()
    await db.refresh(meeting)
    return meeting

async def delete_meeting(db: AsyncSession, meeting_id: int):
    meeting = await get_meeting(db, meeting_id)
    if not meeting:
        return None
    await db.delete(meeting)
    await db.commit()
    return meeting