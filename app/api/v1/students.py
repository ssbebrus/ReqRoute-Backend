from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.schemas.paginated import PaginatedResponse
from app.schemas.student import StudentCreate, StudentUpdate, StudentRead
from app.services.student_service import (
    get_students_filtered,
    get_student,
    create_student,
    update_student,
    delete_student
)
import app.models

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[StudentRead])
async def list_students(request: Request, db: AsyncSession = Depends(get_session)):
    return await get_students_filtered(db, dict(request.query_params))

@router.get("/{student_id}", response_model=StudentRead)
async def read_student(student_id: int, db: AsyncSession = Depends(get_session)):
    student = await get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.post("/", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
async def add_student(data: StudentCreate, db: AsyncSession = Depends(get_session)):
    return await create_student(db, data)

@router.patch("/{student_id}", response_model=StudentRead)
async def edit_student(student_id: int, data: StudentUpdate, db: AsyncSession = Depends(get_session)):
    updated = await update_student(db, student_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Student not found")
    return updated

@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_student(student_id: int, db: AsyncSession = Depends(get_session)):
    deleted = await delete_student(db, student_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Student not found")
