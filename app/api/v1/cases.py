from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.schemas.case import CaseCreate, CaseUpdate, CaseRead
from app.services.case_service import (
    get_all_cases,
    get_case,
    create_case,
    update_case,
    delete_case
)

router = APIRouter()

@router.get("/", response_model=list[CaseRead])
async def list_cases(db: AsyncSession = Depends(get_session)):
    return await get_all_cases(db)

@router.get("/{case_id}", response_model=CaseRead)
async def read_case(case_id: int, db: AsyncSession = Depends(get_session)):
    case = await get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.post("/", response_model=CaseRead, status_code=status.HTTP_201_CREATED)
async def add_case(data: CaseCreate, db: AsyncSession = Depends(get_session)):
    return await create_case(db, data)

@router.patch("/{case_id}", response_model=CaseRead)
async def edit_case(case_id: int, data: CaseUpdate, db: AsyncSession = Depends(get_session)):
    updated = await update_case(db, case_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Case not found")
    return updated

@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_case(case_id: int, db: AsyncSession = Depends(get_session)):
    deleted = await delete_case(db, case_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Case not found")
