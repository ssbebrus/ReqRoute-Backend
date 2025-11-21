from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User

from app.schemas.user import UserCreate, UserUpdate

async def get_all_users(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()

async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, data: UserCreate):
    full_data = data.model_dump()
    full_data['password'] = hash(full_data['password'])
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