from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.schemas.case import CaseCreate, CaseUpdate, CaseRead
from app.services.case_service import (
    get_cases_filtered,
    get_case,
    create_case,
    update_case,
    delete_case
)
from app.schemas.paginated import PaginatedResponse
from app.core.security import security
import app.models

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[CaseRead], dependencies=[Depends(security.access_token_required)])
async def list_cases(request: Request, db: AsyncSession = Depends(get_session)):
    return await get_cases_filtered(db, dict(request.query_params))

@router.get("/{case_id}", response_model=CaseRead, dependencies=[Depends(security.access_token_required)])
async def read_case(case_id: int, db: AsyncSession = Depends(get_session)):
    case = await get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.post("/", response_model=CaseRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(security.access_token_required)])
async def add_case(data: CaseCreate, db: AsyncSession = Depends(get_session)):
    return await create_case(db, data)

@router.patch("/{case_id}", response_model=CaseRead, dependencies=[Depends(security.access_token_required)])
async def edit_case(case_id: int, data: CaseUpdate, db: AsyncSession = Depends(get_session)):
    updated = await update_case(db, case_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Case not found")
    return updated

@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(security.access_token_required)])
async def remove_case(case_id: int, db: AsyncSession = Depends(get_session)):
    deleted = await delete_case(db, case_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Case not found")
