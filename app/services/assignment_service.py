from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.assignment import Assignment

from app.schemas.assignment import AssignmentCreate, AssignmentUpdate

async def get_all_assignments(db: AsyncSession):
    result = await db.execute(select(Assignment))
    return result.scalars().all()

async def get_all_assignments_on_meeting(db: AsyncSession, meeting_id: int):
    result = await db.execute(select(Assignment).where(Assignment.meeting_id == meeting_id))
    return result.scalars().all()

async def get_assignment(db: AsyncSession, assignment_id: int):
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    return result.scalar_one_or_none()

async def create_assignment(db: AsyncSession, data: AssignmentCreate):
    new_assignment = Assignment(**data.model_dump())
    db.add(new_assignment)
    await db.commit()
    await db.refresh(new_assignment)
    return  new_assignment

async def update_assignment(db: AsyncSession, assignment_id: int, data: AssignmentUpdate):
    assignment = await get_assignment(db, assignment_id)
    if not assignment:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(assignment, key, value)
    await db.commit()
    await db.refresh(assignment)
    return assignment

async def delete_assignment(db: AsyncSession, assignment_id: int):
    assignment = await get_assignment(db, assignment_id)
    if not assignment:
        return None
    await db.delete(assignment)
    await db.commit()
    return assignment