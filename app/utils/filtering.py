from sqlalchemy import asc, desc
from sqlalchemy.sql import Select
from sqlalchemy import select

def apply_filters(model, stmt: Select, params: dict):
    for key, value in params.items():
        if value is None:
            continue
        if key.endswith('_contains'):
            field = key.replace('_contains', '')
            column = getattr(model, field, None)
            if column is not None:
                stmt = stmt.where(column.ilike(f'%{value}%'))
            continue
        if key == 'sort':
            column = getattr(model, value.lstrip('-'), None)
            if column is not None:
                stmt = stmt.order_by(
                    desc(column) if value.startswith('-') else column
                )
            continue
        column = getattr(model, key, None)
        if column is not None:
            stmt = stmt.where(column == value)
    return stmt

async def filter_and_paginate(model, db, params: dict):
    stmt = select(model)
    stmt = apply_filters(model, stmt, params)
    page = int(params.get('page', 1))
    page_size = int(params.get('page_size', 20))
    total = (await db.execute(stmt)).unique().scalars().all()
    total_count = len(total)
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    return {
        'total': total_count,
        'page': page,
        'page_size': page_size,
        'items': result.scalars().all()
    }