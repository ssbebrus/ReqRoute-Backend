from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.schemas.term import TermCreate, TermUpdate, TermRead
from app.services.term_service import (
    get_all_terms,
    get_term,
    create_term,
    update_term,
    delete_term
)

router = APIRouter()

@router.get("/", response_model=list[TermRead])
async def list_terms(db: AsyncSession = Depends(get_session)):
    return await get_all_terms(db)

@router.get("/{term_id}", response_model=TermRead)
async def read_term(term_id: int, db: AsyncSession = Depends(get_session)):
    term = await get_term(db, term_id)
    if not term:
        raise HTTPException(status_code=404, detail="Term not found")
    return term

@router.post("/", response_model=TermRead, status_code=status.HTTP_201_CREATED)
async def add_term(data: TermCreate, db: AsyncSession = Depends(get_session)):
    return await create_term(db, data)

@router.patch("/{term_id}", response_model=TermRead)
async def edit_term(term_id: int, data: TermUpdate, db: AsyncSession = Depends(get_session)):
    updated = await update_term(db, term_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Term not found")
    return updated

@router.delete("/{term_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_term(term_id: int, db: AsyncSession = Depends(get_session)):
    deleted = await delete_term(db, term_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Term not found")
