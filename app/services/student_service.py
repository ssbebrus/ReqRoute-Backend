from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.student import Student

from app.schemas.student import StudentCreate, StudentUpdate
from app.utils.filtering import filter_and_paginate


async def get_students_filtered(db: AsyncSession, params: dict):
    return await filter_and_paginate(Student, db, params)

async def get_student(db: AsyncSession, student_id: int):
    result = await db.execute(select(Student).where(Student.id == student_id))
    return result.scalar_one_or_none()

async def create_student(db: AsyncSession, data: StudentCreate):
    new_student = Student(**data.model_dump())
    db.add(new_student)
    await db.commit()
    await db.refresh(new_student)
    return  new_student

async def update_student(db: AsyncSession, student_id: int, data: StudentUpdate):
    student = await get_student(db, student_id)
    if not student:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(student, key, value)
    await db.commit()
    await db.refresh(student)
    return student

async def delete_student(db: AsyncSession, student_id: int):
    student = await get_student(db, student_id)
    if not student:
        return None
    await db.delete(student)
    await db.commit()
    return student