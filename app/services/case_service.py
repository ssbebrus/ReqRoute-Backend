from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.case import Case
from app.schemas.case import CaseCreate, CaseUpdate

async def get_all_cases(db: AsyncSession):
    result = await db.execute(select(Case))
    return result.scalars().all()

async def get_case(db: AsyncSession, case_id: int):
    result = await db.execute(select(Case).where(Case.id == case_id))
    return result.scalar_one_or_none()

async def create_case(db: AsyncSession, data: CaseCreate):
    new_case = Case(**data.model_dump())
    db.add(new_case)
    await db.commit()
    await db.refresh(new_case)
    return  new_case

async def update_case(db: AsyncSession, case_id: int, data: CaseUpdate):
    case = await get_case(db, case_id)
    if not case:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(case, key, value)
    await db.commit()
    await db.refresh(case)
    return case

async def delete_case(db: AsyncSession, case_id: int):
    case = await get_case(db, case_id)
    if not case:
        return None
    await db.delete(case)
    await db.commit()
    return case