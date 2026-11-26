import math
from typing import Annotated, Any

from fastapi import Depends, Query
from pydantic import BaseModel
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from core.errors import AppError

MAX_SORT_FIELDS = 3


class PageParams(BaseModel):
    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def page_params(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PageParams:
    return PageParams(page=page, page_size=page_size)


PageQuery = Annotated[PageParams, Depends(page_params)]


class Page[T](BaseModel):
    items: list[T]
    page: int
    page_size: int
    total: int
    total_pages: int


def parse_sort(sort: str | None, allowed: dict[str, Any], default: str) -> list[Any]:
    """Turn `-posted_at,title` into ORDER BY clauses.

    `allowed` maps public field names to columns. Unknown or excess fields raise `invalid_sort`.
    """
    fields = [f.strip() for f in (sort or default).split(",") if f.strip()]
    if not fields or len(fields) > MAX_SORT_FIELDS:
        raise AppError(422, "invalid_sort", f"Sort accepts 1 to {MAX_SORT_FIELDS} fields.")

    clauses = []
    for field in fields:
        name = field.removeprefix("-")
        if name not in allowed:
            raise AppError(422, "invalid_sort", f"Cannot sort by '{name}'.")
        column = allowed[name]
        clauses.append(column.desc() if field.startswith("-") else column.asc())
    return clauses


def paginate[R](session: Session, query: Select[Any], params: PageParams) -> tuple[list[R], int]:
    """Run `query` for one page and return (rows, total matching rows)."""
    total = session.scalar(select(func.count()).select_from(query.order_by(None).subquery())) or 0
    rows = session.scalars(query.limit(params.page_size).offset(params.offset)).all()
    return list(rows), total


def build_page[T](items: list[T], total: int, params: PageParams) -> Page[T]:
    return Page[T](
        items=items,
        page=params.page,
        page_size=params.page_size,
        total=total,
        total_pages=math.ceil(total / params.page_size),
    )
