import hashlib

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserLogin, UserRead
from app.core.security import security


async def user_login(db: AsyncSession, data: UserLogin):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user:
        return None
    hashed_password = hashlib.sha256(data.password.encode('utf-8')).hexdigest()
    if hashed_password != user.password:
        return None
    access_token = security.create_access_token(str(user.id))
    return access_token
