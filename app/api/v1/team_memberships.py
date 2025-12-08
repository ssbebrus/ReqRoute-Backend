from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.schemas.paginated import PaginatedResponse
from app.schemas.team_membership import TeamMembershipCreate, TeamMembershipUpdate, TeamMembershipRead
from app.services.team_membership_service import (
    get_memberships_filtered,
    get_membership,
    create_membership,
    update_membership,
    delete_membership
)
import app.models

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[TeamMembershipRead])
async def list_team_memberships(request: Request, db: AsyncSession = Depends(get_session)):
    return await get_memberships_filtered(db, dict(request.query_params))

@router.get("/{team_membership_id}", response_model=TeamMembershipRead)
async def read_team_membership(team_membership_id: int, db: AsyncSession = Depends(get_session)):
    team_membership = await get_membership(db, team_membership_id)
    if not team_membership:
        raise HTTPException(status_code=404, detail="TeamMembership not found")
    return team_membership

@router.post("/", response_model=TeamMembershipRead, status_code=status.HTTP_201_CREATED)
async def add_team_membership(data: TeamMembershipCreate, db: AsyncSession = Depends(get_session)):
    return await create_membership(db, data)

@router.patch("/{team_membership_id}", response_model=TeamMembershipRead)
async def edit_team_membership(team_membership_id: int, data: TeamMembershipUpdate, db: AsyncSession = Depends(get_session)):
    updated = await update_membership(db, team_membership_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="TeamMembership not found")
    return updated

@router.delete("/{team_membership_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_membership(team_membership_id: int, db: AsyncSession = Depends(get_session)):
    deleted = await delete_membership(db, team_membership_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="TeamMembership not found")
