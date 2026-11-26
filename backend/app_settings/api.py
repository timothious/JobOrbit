from fastapi import APIRouter

from app_settings.schemas import AppSettings
from app_settings.service import get_app_settings, save_app_settings
from core.deps import UowDep

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("")
def read_settings(uow: UowDep) -> AppSettings:
    return get_app_settings(uow.session)


@router.put("")
def replace_settings(body: AppSettings, uow: UowDep) -> AppSettings:
    save_app_settings(uow.session, body)
    uow.commit()
    return body
