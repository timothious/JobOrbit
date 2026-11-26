from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, Field

from core.validation import CountryCode, Timezone


def _not_blank(value: str) -> str:
    if not value.strip():
        raise ValueError("must not be only whitespace")
    return value


Password = Annotated[str, Field(min_length=12, max_length=128), AfterValidator(_not_blank)]


class SetupProfile(BaseModel):
    full_name: Annotated[str | None, Field(max_length=120)] = None
    citizenship_country_codes: Annotated[list[CountryCode], Field(max_length=10)] = []
    residence_country_code: CountryCode | None = None


class SetupRequest(BaseModel):
    password: Password
    profile: SetupProfile = SetupProfile()
    timezone: Timezone = "UTC"


class LoginRequest(BaseModel):
    password: Annotated[str, Field(max_length=128)]


class ChangePasswordRequest(BaseModel):
    current_password: Annotated[str, Field(max_length=128)]
    new_password: Password


class AuthStatus(BaseModel):
    setup_complete: bool
    authenticated: bool


class SessionInfo(BaseModel):
    csrf_token: str
    expires_at: datetime
