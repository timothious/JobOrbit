"""Idempotent loader for bundled reference data (countries, regions, skills)."""

import json
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from catalog.models import Country, RegionMember, Skill

DATA_DIR = Path(__file__).parent / "data"

# Columns refreshed from the bundled file; user-curated columns (english_status, ...) are kept.
COUNTRY_FILE_COLUMNS = (
    "iso3",
    "name",
    "official_name",
    "region",
    "subregion",
    "currency_code",
    "languages",
)


def normalize_skill_name(name: str) -> str:
    return " ".join(name.lower().replace("_", " ").split())


def _load(name: str) -> Any:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def seed_reference_data(session: Session) -> None:
    _seed_countries(session)
    _seed_regions(session)
    _seed_skills(session)


def _seed_countries(session: Session) -> None:
    existing = {c.code: c for c in session.scalars(select(Country))}
    for row in _load("countries.json"):
        country = existing.get(row["code"]) or Country(code=row["code"])
        for column in COUNTRY_FILE_COLUMNS:
            setattr(country, column, row[column])
        session.add(country)
    session.flush()


def _seed_regions(session: Session) -> None:
    # Region membership is editable via the data file only (MVP), so the file is the truth.
    session.execute(delete(RegionMember))
    for region_code, members in _load("regions.json").items():
        session.add_all(RegionMember(region_code=region_code, country_code=c) for c in members)
    session.flush()


def _seed_skills(session: Session) -> None:
    existing = {s.normalized_name: s for s in session.scalars(select(Skill))}
    for row in _load("skills.json"):
        normalized = normalize_skill_name(row["name"])
        skill = existing.get(normalized)
        if skill is None:
            session.add(Skill(normalized_name=normalized, is_system=True, **row))
        elif skill.is_system:
            skill.name, skill.category, skill.aliases = row["name"], row["category"], row["aliases"]
    session.flush()
