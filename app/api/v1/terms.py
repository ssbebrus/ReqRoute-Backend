from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import security
from app.db.session import get_session
from app.schemas.paginated import PaginatedResponse
from app.schemas.term import TermCreate, TermUpdate, TermRead
from app.services.term_service import (
    get_terms_filtered,
    get_term,
    create_term,
    update_term,
    delete_term
)
import app.models

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[TermRead], dependencies=[Depends(security.access_token_required)])
async def list_terms(request: Request, db: AsyncSession = Depends(get_session)):
    return await get_terms_filtered(db, dict(request.query_params))

@router.get("/{term_id}", response_model=TermRead, dependencies=[Depends(security.access_token_required)])
async def read_term(term_id: int, db: AsyncSession = Depends(get_session)):
    term = await get_term(db, term_id)
    if not term:
        raise HTTPException(status_code=404, detail="Term not found")
    return term

@router.post("/", response_model=TermRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(security.access_token_required)])
async def add_term(data: TermCreate, db: AsyncSession = Depends(get_session)):
    return await create_term(db, data)

@router.patch("/{term_id}", response_model=TermRead, dependencies=[Depends(security.access_token_required)])
async def edit_term(term_id: int, data: TermUpdate, db: AsyncSession = Depends(get_session)):
    updated = await update_term(db, term_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Term not found")
    return updated

@router.delete("/{term_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(security.access_token_required)])
async def remove_term(term_id: int, db: AsyncSession = Depends(get_session)):
    deleted = await delete_term(db, term_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Term not found")
