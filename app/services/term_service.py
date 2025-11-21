from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.term import Term
from app.schemas.term import TermCreate, TermUpdate

async def get_all_terms(db: AsyncSession):
    result = await db.execute(select(Term))
    return result.scalars().all()

async def get_term(db: AsyncSession, term_id: int):
    result = await db.execute(select(Term).where(Term.id == term_id))
    return result.scalar_one_or_none()

async def create_term(db: AsyncSession, data: TermCreate):
    new_term = Term(**data.model_dump())
    db.add(new_term)
    await db.commit()
    await db.refresh(new_term)
    return  new_term

async def update_term(db: AsyncSession, term_id: int, data: TermUpdate):
    term = await get_term(db, term_id)
    if not term:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(term, key, value)
    await db.commit()
    await db.refresh(term)
    return term

async def delete_term(db: AsyncSession, term_id: int):
    term = await get_term(db, term_id)
    if not term:
        return None
    await db.delete(term)
    await db.commit()
    return term