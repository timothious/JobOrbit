from datetime import datetime
from typing import Any

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from core.base import Base, TimestampMixin, check_in

ENGLISH_STATUSES = ("official", "widely_used_in_business", "limited", "unknown")
SKILL_CATEGORIES = (
    "programming_language", "framework", "library", "tool", "cloud", "database",
    "data", "ml_ai", "devops", "soft", "domain", "other",
)  # fmt: skip


class Country(TimestampMixin, Base):
    __tablename__ = "countries"
    __table_args__ = (check_in("english_status", ENGLISH_STATUSES),)

    code: Mapped[str] = mapped_column(String(2), primary_key=True)
    iso3: Mapped[str] = mapped_column(String(3), unique=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    official_name: Mapped[str | None] = mapped_column(String(200))
    region: Mapped[str | None] = mapped_column(String(50), index=True)
    subregion: Mapped[str | None] = mapped_column(String(80))
    currency_code: Mapped[str | None] = mapped_column(String(3))
    languages: Mapped[list[Any]] = mapped_column(default=list)
    english_status: Mapped[str] = mapped_column(String(30), default="unknown")
    english_status_verified_at: Mapped[datetime | None]
    demonym: Mapped[str | None] = mapped_column(String(80))
    is_active: Mapped[bool] = mapped_column(default=True)


class RegionMember(TimestampMixin, Base):
    __tablename__ = "region_members"

    region_code: Mapped[str] = mapped_column(String(20), primary_key=True)
    country_code: Mapped[str] = mapped_column(ForeignKey("countries.code"), primary_key=True)


class Skill(TimestampMixin, Base):
    __tablename__ = "skills"
    __table_args__ = (check_in("category", SKILL_CATEGORIES),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    normalized_name: Mapped[str] = mapped_column(String(100), unique=True)
    category: Mapped[str | None] = mapped_column(String(20))
    aliases: Mapped[list[Any]] = mapped_column(default=list)
    is_system: Mapped[bool] = mapped_column(default=True)
