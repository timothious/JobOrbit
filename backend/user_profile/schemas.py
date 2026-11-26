from datetime import datetime
from typing import Annotated, Self

from pydantic import BaseModel, Field, model_validator

from core.validation import CountryCode


class Citizenship(BaseModel):
    country_code: CountryCode
    is_primary: bool = False


class ProfileOut(BaseModel):
    full_name: str | None
    residence_country_code: str | None
    citizenships: list[Citizenship]
    profile_version: int
    updated_at: datetime


class ProfilePatch(BaseModel):
    """Minimal P1 profile (T1.8). Omitted fields are left unchanged; lists replace."""

    full_name: Annotated[str | None, Field(max_length=120)] = None
    residence_country_code: CountryCode | None = None
    citizenships: Annotated[list[Citizenship], Field(max_length=10)] | None = None

    @model_validator(mode="after")
    def _valid_citizenships(self) -> Self:
        if self.citizenships is None:
            return self
        codes = [c.country_code for c in self.citizenships]
        if len(codes) != len(set(codes)):
            raise ValueError("citizenships must not contain duplicates")
        if sum(c.is_primary for c in self.citizenships) > 1:
            raise ValueError("at most one citizenship can be primary")
        return self
