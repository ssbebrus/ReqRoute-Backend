from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
import hashlib
from app.schemas.user import UserCreate, UserUpdate
from app.utils.filtering import filter_and_paginate


async def get_users_filtered(db: AsyncSession, params: dict):
    return await filter_and_paginate(User, db, params)

async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, data: UserCreate):
    full_data = data.model_dump()
    full_data['password'] = hashlib.sha256(full_data['password'].encode('utf-8')).hexdigest()
    new_user = User(**full_data)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return  new_user

async def update_user(db: AsyncSession, user_id: int, data: UserUpdate):
    user = await get_user(db, user_id)
    if not user:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user

async def delete_user(db: AsyncSession, user_id: int):
    user = await get_user(db, user_id)
    if not user:
        return None
    await db.delete(user)
    await db.commit()
    return user