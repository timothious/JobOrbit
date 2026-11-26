from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from catalog.models import Country
from core.errors import AppError


def ensure_countries_exist(session: Session, codes: Iterable[str | None], field: str) -> None:
    wanted = {c for c in codes if c}
    if not wanted:
        return
    found = set(session.scalars(select(Country.code).where(Country.code.in_(wanted))))
    missing = sorted(wanted - found)
    if missing:
        raise AppError(
            422,
            "validation_error",
            "Request validation failed.",
            [
                {"field": field, "code": "unknown_country", "message": f"Unknown country: {c}"}
                for c in missing
            ],
        )
