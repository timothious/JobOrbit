from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CountryOption(BaseModel):
    code: str
    name: str


class CountryListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    region: str | None
    subregion: str | None
    currency_code: str | None
    english_status: str
    english_status_verified_at: datetime | None


class CountryDetail(CountryListItem):
    iso3: str
    official_name: str | None
    languages: list[str]
    region_codes: list[str]
