from sqlalchemy import select
from sqlalchemy.orm import Session

from app_settings.models import AppSetting
from app_settings.schemas import AppSettings


def get_app_settings(session: Session) -> AppSettings:
    stored = {row.key: row.value for row in session.scalars(select(AppSetting))}
    known = {k: v for k, v in stored.items() if k in AppSettings.model_fields}
    return AppSettings.model_validate(known)


def save_app_settings(session: Session, settings: AppSettings) -> None:
    for key, value in settings.model_dump(mode="json").items():
        session.merge(AppSetting(key=key, value=value))
    session.flush()
