from sqlalchemy.orm import Session

from catalog.service import ensure_countries_exist
from user_profile.models import PROFILE_ID, ProfileCitizenship, UserProfile
from user_profile.schemas import Citizenship, ProfilePatch


def get_profile(session: Session) -> UserProfile:
    profile = session.get(UserProfile, PROFILE_ID)
    if profile is None:  # Created at setup; recreated empty if it was ever removed.
        profile = UserProfile(id=PROFILE_ID)
        session.add(profile)
        session.flush()
    return profile


def create_profile(
    session: Session, full_name: str | None, citizenship_codes: list[str], residence: str | None
) -> UserProfile:
    citizenships = [
        Citizenship(country_code=c, is_primary=i == 0)
        for i, c in enumerate(dict.fromkeys(citizenship_codes))
    ]
    return update_profile(
        session,
        ProfilePatch(
            full_name=full_name, residence_country_code=residence, citizenships=citizenships
        ),
    )


def update_profile(session: Session, patch: ProfilePatch) -> UserProfile:
    fields = patch.model_fields_set
    ensure_countries_exist(session, [patch.residence_country_code], "residence_country_code")
    if patch.citizenships is not None:
        ensure_countries_exist(
            session, [c.country_code for c in patch.citizenships], "citizenships"
        )

    profile = get_profile(session)
    scoring_changed = False

    if "full_name" in fields:
        profile.full_name = patch.full_name
    if (
        "residence_country_code" in fields
        and patch.residence_country_code != profile.residence_country_code
    ):
        profile.residence_country_code = patch.residence_country_code
        scoring_changed = True
    if "citizenships" in fields:
        new = [(c.country_code, c.is_primary) for c in patch.citizenships or []]
        old = [(c.country_code, c.is_primary) for c in profile.citizenships]
        if new != old:
            profile.citizenships.clear()
            session.flush()  # free the (profile_id, country_code) unique keys before re-inserting
            profile.citizenships.extend(
                ProfileCitizenship(country_code=code, is_primary=primary) for code, primary in new
            )
            scoring_changed = True

    if scoring_changed:  # FR-060: bump only on scoring-relevant changes
        profile.profile_version += 1
    session.flush()
    session.refresh(profile)
    return profile
