from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.schemas.user import UserLogin
from app.services.auth_service import (
    user_login
)
from app.core.security import security
import app.models

router = APIRouter()

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(response: Response, data: UserLogin, db: AsyncSession = Depends(get_session)):
    access_token = await user_login(db, data)
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    response.set_cookie(key="access_token", value=access_token)
    return {"access_token": access_token}


