from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy import select

from catalog.models import Country, RegionMember
from catalog.schemas import CountryDetail, CountryListItem, CountryOption
from core.deps import UowDep
from core.errors import AppError
from core.pagination import Page, PageQuery, build_page, paginate, parse_sort

router = APIRouter(prefix="/countries", tags=["countries"])
# Registered with a different auth dependency (see main_api): usable by the setup form.
options_router = APIRouter(prefix="/countries", tags=["countries"])

SORT_FIELDS = {"name": Country.name, "code": Country.code, "region": Country.region}


@options_router.get("/options")
def country_options(uow: UowDep) -> list[CountryOption]:
    """All active countries as `{code, name}`, for pickers."""
    rows = uow.session.execute(
        select(Country.code, Country.name).where(Country.is_active).order_by(Country.name)
    )
    return [CountryOption(code=code, name=name) for code, name in rows]


@router.get("")
def list_countries(
    uow: UowDep,
    page: PageQuery,
    q: Annotated[str | None, Query(max_length=200)] = None,
    region: Annotated[list[str] | None, Query()] = None,
    sort: str | None = None,
) -> Page[CountryListItem]:
    """Country Explorer list (§5.1). Job, salary, pathway and score columns arrive in P2–P4."""
    query = select(Country).where(Country.is_active)
    if q:
        query = query.where(Country.name.ilike(f"%{q.strip()}%"))
    regions = [r.strip().upper() for value in region or [] for r in value.split(",") if r.strip()]
    if regions:
        members = select(RegionMember.country_code).where(RegionMember.region_code.in_(regions))
        query = query.where(Country.code.in_(members))
    query = query.order_by(*parse_sort(sort, SORT_FIELDS, default="name"))

    rows: list[Country]
    rows, total = paginate(uow.session, query, page)
    return build_page([CountryListItem.model_validate(c) for c in rows], total, page)


@router.get("/{code}")
def get_country(code: str, uow: UowDep) -> CountryDetail:
    country = uow.session.get(Country, code.upper())
    if country is None:
        raise AppError(404, "not_found", f"Country '{code}' not found.")
    region_codes = uow.session.scalars(
        select(RegionMember.region_code)
        .where(RegionMember.country_code == country.code)
        .order_by(RegionMember.region_code)
    ).all()
    return CountryDetail.model_validate(
        {
            **CountryListItem.model_validate(country).model_dump(),
            "iso3": country.iso3,
            "official_name": country.official_name,
            "languages": country.languages,
            "region_codes": list(region_codes),
        }
    )
