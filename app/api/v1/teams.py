from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.schemas.paginated import PaginatedResponse
from app.schemas.team import TeamCreate, TeamUpdate, TeamRead
from app.services.team_service import (
    get_teams_filtered,
    get_team,
    create_team,
    update_team,
    delete_team
)
import app.models

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[TeamRead])
async def list_teams(request: Request, db: AsyncSession = Depends(get_session)):
    return await get_teams_filtered(db, dict(request.query_params))

@router.get("/{team_id}", response_model=TeamRead)
async def read_team(team_id: int, db: AsyncSession = Depends(get_session)):
    team = await get_team(db, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@router.post("/", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
async def add_team(data: TeamCreate, db: AsyncSession = Depends(get_session)):
    return await create_team(db, data)

@router.patch("/{team_id}", response_model=TeamRead)
async def edit_team(team_id: int, data: TeamUpdate, db: AsyncSession = Depends(get_session)):
    updated = await update_team(db, team_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Team not found")
    return updated

@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team(team_id: int, db: AsyncSession = Depends(get_session)):
    deleted = await delete_team(db, team_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Team not found")
