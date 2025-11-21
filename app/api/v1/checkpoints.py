from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.schemas.checkpoint import CheckpointCreate, CheckpointUpdate, CheckpointRead
from app.services.checkpoint_service import (
    get_all_checkpoints,
    get_all_checkpoints_on_team,
    get_checkpoint,
    create_checkpoint,
    update_checkpoint,
    delete_checkpoint
)
import app.models

router = APIRouter()

@router.get("/", response_model=list[CheckpointRead])
async def list_checkpoints(db: AsyncSession = Depends(get_session)):
    return await get_all_checkpoints(db)

@router.get("/team/{team_id}", response_model=list[CheckpointRead])
async def list_checkpoints_on_team(team_id: int, db: AsyncSession = Depends(get_session)):
    return await get_all_checkpoints_on_team(db, team_id)

@router.get("/{checkpoint_id}", response_model=CheckpointRead)
async def read_checkpoint(checkpoint_id: int, db: AsyncSession = Depends(get_session)):
    checkpoint = await get_checkpoint(db, checkpoint_id)
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    return checkpoint

@router.post("/", response_model=CheckpointRead, status_code=status.HTTP_201_CREATED)
async def add_checkpoint(data: CheckpointCreate, db: AsyncSession = Depends(get_session)):
    return await create_checkpoint(db, data)

@router.patch("/{checkpoint_id}", response_model=CheckpointRead)
async def edit_checkpoint(checkpoint_id: int, data: CheckpointUpdate, db: AsyncSession = Depends(get_session)):
    updated = await update_checkpoint(db, checkpoint_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    return updated

@router.delete("/{checkpoint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_checkpoint(checkpoint_id: int, db: AsyncSession = Depends(get_session)):
    deleted = await delete_checkpoint(db, checkpoint_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
