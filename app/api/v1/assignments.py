from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.schemas.assignment import AssignmentCreate, AssignmentUpdate, AssignmentRead
from app.services.assignment_service import (
    get_assignments_filtered,
    get_assignment,
    create_assignment,
    update_assignment,
    delete_assignment
)
from app.schemas.paginated import PaginatedResponse
import app.models

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[AssignmentRead])
async def list_assignments(request: Request, db: AsyncSession = Depends(get_session)):
    return await get_assignments_filtered(db, dict(request.query_params))

@router.get("/{assignment_id}", response_model=AssignmentRead)
async def read_assignment(assignment_id: int, db: AsyncSession = Depends(get_session)):
    assignment = await get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment

@router.post("/", response_model=AssignmentRead, status_code=status.HTTP_201_CREATED)
async def add_assignment(data: AssignmentCreate, db: AsyncSession = Depends(get_session)):
    return await create_assignment(db, data)

@router.patch("/{assignment_id}", response_model=AssignmentRead)
async def edit_assignment(assignment_id: int, data: AssignmentUpdate, db: AsyncSession = Depends(get_session)):
    updated = await update_assignment(db, assignment_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return updated

@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_assignment(assignment_id: int, db: AsyncSession = Depends(get_session)):
    deleted = await delete_assignment(db, assignment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Assignment not found")
