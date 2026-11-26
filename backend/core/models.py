"""Imports every model module so `Base.metadata` is complete (Alembic, tests)."""

from app_settings import models as app_settings_models
from auth import models as auth_models
from catalog import models as catalog_models
from core.base import Base
from ingestion import models as ingestion_models
from user_profile import models as user_profile_models

__all__ = [
    "Base",
    "app_settings_models",
    "auth_models",
    "catalog_models",
    "ingestion_models",
    "user_profile_models",
]
