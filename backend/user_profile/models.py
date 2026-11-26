from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base import Base, TimestampMixin

PROFILE_ID = 1


class UserProfile(TimestampMixin, Base):
    """Singleton profile. Only P1 columns exist; the rest arrive with the full profile (T4.1)."""

    __tablename__ = "user_profile"
    __table_args__ = (CheckConstraint("id = 1", name="singleton"),)

    id: Mapped[int] = mapped_column(primary_key=True, default=PROFILE_ID)
    full_name: Mapped[str | None] = mapped_column(String(120))
    residence_country_code: Mapped[str | None] = mapped_column(ForeignKey("countries.code"))
    profile_version: Mapped[int] = mapped_column(default=1)

    citizenships: Mapped[list["ProfileCitizenship"]] = relationship(
        cascade="all, delete-orphan", order_by="ProfileCitizenship.id"
    )


class ProfileCitizenship(TimestampMixin, Base):
    __tablename__ = "profile_citizenships"
    __table_args__ = (UniqueConstraint("profile_id", "country_code"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("user_profile.id", ondelete="CASCADE"))
    country_code: Mapped[str] = mapped_column(ForeignKey("countries.code"))
    is_primary: Mapped[bool] = mapped_column(default=False)
