import pytest
from sqlalchemy import Integer, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from core.errors import AppError
from core.pagination import PageParams, build_page, paginate, parse_sort


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


ALLOWED = {"id": Item.id}


def test_offset_is_derived_from_page() -> None:
    assert PageParams(page=3, page_size=20).offset == 40


def test_parse_sort_supports_descending_prefix() -> None:
    clauses = parse_sort("-id", ALLOWED, default="id")
    assert str(clauses[0]) == "items.id DESC"
    assert str(parse_sort(None, ALLOWED, default="id")[0]) == "items.id ASC"


@pytest.mark.parametrize("sort", ["nope", "id,id,id,id"])
def test_parse_sort_rejects_unknown_and_excess_fields(sort: str) -> None:
    allowed = {"id": Item.id}
    with pytest.raises(AppError) as exc:
        parse_sort(sort, allowed, default="id")
    assert exc.value.code == "invalid_sort"
    assert exc.value.status_code == 422


def test_paginate_returns_page_slice_and_total() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all(Item(id=i) for i in range(1, 46))
        session.commit()

        params = PageParams(page=3, page_size=20)
        query = select(Item.id).order_by(*parse_sort("id", ALLOWED, default="id"))
        rows: list[int]
        rows, total = paginate(session, query, params)

    assert rows == [41, 42, 43, 44, 45]
    page = build_page(rows, total, params)
    assert (page.total, page.total_pages, page.page) == (45, 3, 3)


def test_empty_result_has_zero_pages() -> None:
    assert build_page([], 0, PageParams(page=1, page_size=20)).total_pages == 0
