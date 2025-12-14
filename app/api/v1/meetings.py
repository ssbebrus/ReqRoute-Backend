from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import security
from app.db.session import get_session
from app.schemas.meeting import MeetingCreate, MeetingUpdate, MeetingRead
from app.schemas.meeting_user import MeetingUserCreate, MeetingUserRead
from app.schemas.paginated import PaginatedResponse
from app.services.meeting_service import (
    get_meetings_filtered,
    get_previous_meeting_id,
    get_meeting,
    create_meeting,
    update_meeting,
    delete_meeting,
    link_meeting_user,
    get_team_schedule,
    create_meeting_schedule,
    update_meeting_schedule,
)
from app.schemas.meeting_schedule import (
    MeetingScheduleCreate,
    MeetingScheduleUpdate,
    MeetingScheduleRead,
)
import app.models

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[MeetingRead], dependencies=[Depends(security.access_token_required)])
async def list_meetings(request: Request, db: AsyncSession = Depends(get_session)):
    return await get_meetings_filtered(db, dict(request.query_params))

@router.get("/previous/{meeting_id}", response_model=list[MeetingRead], dependencies=[Depends(security.access_token_required)])
async def read_previous_meeting_id(meeting_id: int, db: AsyncSession = Depends(get_session)):
    return await get_previous_meeting_id(db, meeting_id)

@router.get("/{meeting_id}", response_model=MeetingRead, dependencies=[Depends(security.access_token_required)])
async def read_meeting(meeting_id: int, db: AsyncSession = Depends(get_session)):
    meeting = await get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

@router.post("/", response_model=MeetingRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(security.access_token_required)])
async def add_meeting(data: MeetingCreate, db: AsyncSession = Depends(get_session)):
    return await create_meeting(db, data)

@router.post("/user-link/", response_model=MeetingUserRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(security.access_token_required)])
async def add_meeting_user_link(data: MeetingUserCreate, db: AsyncSession = Depends(get_session)):
    return await link_meeting_user(db, data)

@router.patch("/{meeting_id}", response_model=MeetingRead, dependencies=[Depends(security.access_token_required)])
async def edit_meeting(meeting_id: int, data: MeetingUpdate, db: AsyncSession = Depends(get_session)):
    updated = await update_meeting(db, meeting_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return updated

@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(security.access_token_required)])
async def remove_meeting(meeting_id: int, db: AsyncSession = Depends(get_session)):
    deleted = await delete_meeting(db, meeting_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Meeting not found")


@router.get("/schedule/team/{team_id}", response_model=MeetingScheduleRead, dependencies=[Depends(security.access_token_required)])
async def get_schedule(team_id: int, db: AsyncSession = Depends(get_session)):
    schedule = await get_team_schedule(db, team_id)
    if not schedule:
        raise HTTPException(
            status_code=404, detail="No active schedule found for this team"
        )
    return schedule


@router.post("/schedule/", response_model=MeetingScheduleRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(security.access_token_required)])
async def create_schedule(data: MeetingScheduleCreate, db: AsyncSession = Depends(get_session)):
    try:
        return await create_meeting_schedule(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/schedule/{schedule_id}", response_model=MeetingScheduleRead, dependencies=[Depends(security.access_token_required)])
async def update_schedule(schedule_id: int, data: MeetingScheduleUpdate, db: AsyncSession = Depends(get_session)):
    updated = await update_meeting_schedule(db, schedule_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return updated
