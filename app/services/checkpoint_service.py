from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.checkpoint import Checkpoint

from app.schemas.checkpoint import CheckpointCreate, CheckpointUpdate
from app.utils.filtering import filter_and_paginate


async def get_checkpoints_filtered(db: AsyncSession, params: dict):
    return await filter_and_paginate(Checkpoint, db, params)

async def get_checkpoint(db: AsyncSession, checkpoint_id: int):
    result = await db.execute(select(Checkpoint).where(Checkpoint.id == checkpoint_id))
    return result.scalar_one_or_none()

async def create_checkpoint(db: AsyncSession, data: CheckpointCreate):
    new_checkpoint = Checkpoint(**data.model_dump())
    db.add(new_checkpoint)
    await db.commit()
    await db.refresh(new_checkpoint)
    return  new_checkpoint

async def update_checkpoint(db: AsyncSession, checkpoint_id: int, data: CheckpointUpdate):
    checkpoint = await get_checkpoint(db, checkpoint_id)
    if not checkpoint:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(checkpoint, key, value)
    await db.commit()
    await db.refresh(checkpoint)
    return checkpoint

async def delete_checkpoint(db: AsyncSession, checkpoint_id: int):
    checkpoint = await get_checkpoint(db, checkpoint_id)
    if not checkpoint:
        return None
    await db.delete(checkpoint)
    await db.commit()
    return checkpoint