from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.schemas.user import UserCreate, UserUpdate, UserRead
from app.services.user_service import (
    get_all_users,
    get_user,
    create_user,
    update_user,
    delete_user
)
import app.models

router = APIRouter()

@router.get("/", response_model=list[UserRead])
async def list_users(db: AsyncSession = Depends(get_session)):
    return await get_all_users(db)

@router.get("/{user_id}", response_model=UserRead)
async def read_user(user_id: int, db: AsyncSession = Depends(get_session)):
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def add_user(data: UserCreate, db: AsyncSession = Depends(get_session)):
    return await create_user(db, data)

@router.patch("/{user_id}", response_model=UserRead)
async def edit_user(user_id: int, data: UserUpdate, db: AsyncSession = Depends(get_session)):
    updated = await update_user(db, user_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user(user_id: int, db: AsyncSession = Depends(get_session)):
    deleted = await delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
