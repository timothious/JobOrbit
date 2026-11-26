from fastapi import APIRouter

from core.deps import UowDep
from user_profile.models import UserProfile
from user_profile.schemas import Citizenship, ProfileOut, ProfilePatch
from user_profile.service import get_profile, update_profile

router = APIRouter(prefix="/profile", tags=["profile"])


def _out(profile: UserProfile) -> ProfileOut:
    return ProfileOut(
        full_name=profile.full_name,
        residence_country_code=profile.residence_country_code,
        citizenships=[
            Citizenship(country_code=c.country_code, is_primary=c.is_primary)
            for c in profile.citizenships
        ],
        profile_version=profile.profile_version,
        updated_at=profile.updated_at,
    )


@router.get("")
def read_profile(uow: UowDep) -> ProfileOut:
    profile = get_profile(uow.session)
    uow.commit()
    return _out(profile)


@router.patch("")
def patch_profile(body: ProfilePatch, uow: UowDep) -> ProfileOut:
    profile = update_profile(uow.session, body)
    uow.commit()
    return _out(profile)
