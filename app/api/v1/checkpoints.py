from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import security
from app.db.session import get_session
from app.schemas.checkpoint import CheckpointCreate, CheckpointUpdate, CheckpointRead
from app.schemas.paginated import PaginatedResponse
from app.services.checkpoint_service import (
    get_checkpoints_filtered,
    get_checkpoint,
    create_checkpoint,
    update_checkpoint,
    delete_checkpoint
)
import app.models

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[CheckpointRead], dependencies=[Depends(security.access_token_required)])
async def list_checkpoints(request: Request, db: AsyncSession = Depends(get_session)):
    return await get_checkpoints_filtered(db, dict(request.query_params))

@router.get("/{checkpoint_id}", response_model=CheckpointRead, dependencies=[Depends(security.access_token_required)])
async def read_checkpoint(checkpoint_id: int, db: AsyncSession = Depends(get_session)):
    checkpoint = await get_checkpoint(db, checkpoint_id)
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    return checkpoint

@router.post("/", response_model=CheckpointRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(security.access_token_required)])
async def add_checkpoint(data: CheckpointCreate, db: AsyncSession = Depends(get_session)):
    return await create_checkpoint(db, data)

@router.patch("/{checkpoint_id}", response_model=CheckpointRead, dependencies=[Depends(security.access_token_required)])
async def edit_checkpoint(checkpoint_id: int, data: CheckpointUpdate, db: AsyncSession = Depends(get_session)):
    updated = await update_checkpoint(db, checkpoint_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    return updated

@router.delete("/{checkpoint_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(security.access_token_required)])
async def remove_checkpoint(checkpoint_id: int, db: AsyncSession = Depends(get_session)):
    deleted = await delete_checkpoint(db, checkpoint_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
