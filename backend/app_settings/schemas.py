from typing import Annotated, Literal, Self

from pydantic import BaseModel, Field, model_validator

from core.validation import CurrencyCode, Timezone


class Retention(BaseModel):
    expired_job_days: Annotated[int, Field(ge=30, le=3650)] = 180
    sync_log_days: Annotated[int, Field(ge=7, le=3650)] = 180
    read_notification_days: Annotated[int, Field(ge=7, le=3650)] = 90
    unread_notification_days: Annotated[int, Field(ge=7, le=3650)] = 180
    noncurrent_score_days: Annotated[int, Field(ge=7, le=3650)] = 30
    raw_payload_days: Annotated[int, Field(ge=1, le=365)] = 30


class Freshness(BaseModel):
    pathway_fresh_days: Annotated[int, Field(gt=0)] = 180
    pathway_outdated_days: Annotated[int, Field(le=1825)] = 365

    @model_validator(mode="after")
    def _ordered(self) -> Self:
        if self.pathway_fresh_days >= self.pathway_outdated_days:
            raise ValueError("pathway_fresh_days must be less than pathway_outdated_days")
        return self


class AppSettings(BaseModel):
    """API Specification §15.1. Missing keys fall back to these defaults."""

    timezone: Timezone = "UTC"
    display_currency: CurrencyCode = "USD"
    reference_currency: CurrencyCode = "USD"
    new_job_window_days: Annotated[int, Field(ge=1, le=30)] = 7
    default_page_size: Literal[20, 50, 100] = 20
    analytics_default_period_days: Literal[30, 90, 365] = 90
    fx_auto_refresh: bool = True
    retention: Retention = Retention()
    freshness: Freshness = Freshness()
