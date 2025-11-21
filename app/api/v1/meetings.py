from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.schemas.meeting import MeetingCreate, MeetingUpdate, MeetingRead
from app.schemas.meeting_user import MeetingUserCreate, MeetingUserRead
from app.services.meeting_service import (
    get_all_meetings,
    get_all_meetings_on_team,
    get_previous_meeting_id,
    get_meeting,
    create_meeting,
    update_meeting,
    delete_meeting,
    link_meeting_user
)
import app.models

router = APIRouter()

@router.get("/", response_model=list[MeetingRead])
async def list_meetings(db: AsyncSession = Depends(get_session)):
    return await get_all_meetings(db)

@router.get("/team/{team_id}", response_model=list[MeetingRead])
async def list_meetings_on_team(team_id: int, db: AsyncSession = Depends(get_session)):
    return await get_all_meetings_on_team(db, team_id)

@router.get("/previous/{meeting_id}", response_model=list[MeetingRead])
async def read_previous_meeting_id(meeting_id: int, db: AsyncSession = Depends(get_session)):
    return await get_previous_meeting_id(db, meeting_id)

@router.get("/{meeting_id}", response_model=MeetingRead)
async def read_meeting(meeting_id: int, db: AsyncSession = Depends(get_session)):
    meeting = await get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

@router.post("/", response_model=MeetingRead, status_code=status.HTTP_201_CREATED)
async def add_meeting(data: MeetingCreate, db: AsyncSession = Depends(get_session)):
    return await create_meeting(db, data)

@router.post("/user-link/", response_model=MeetingUserRead, status_code=status.HTTP_201_CREATED)
async def add_meeting_user_link(data: MeetingUserCreate, db: AsyncSession = Depends(get_session)):
    return await link_meeting_user(db, data)

@router.patch("/{meeting_id}", response_model=MeetingRead)
async def edit_meeting(meeting_id: int, data: MeetingUpdate, db: AsyncSession = Depends(get_session)):
    updated = await update_meeting(db, meeting_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return updated

@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_meeting(meeting_id: int, db: AsyncSession = Depends(get_session)):
    deleted = await delete_meeting(db, meeting_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Meeting not found")
