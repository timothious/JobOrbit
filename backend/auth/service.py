from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from auth.models import AuthCredential, AuthSession
from auth.security import hash_password, hash_token, new_token, verify_password
from core.config import Settings
from core.errors import AppError

SINGLETON_ID = 1
LAST_SEEN_RESOLUTION = timedelta(minutes=1)


@dataclass(frozen=True)
class NewSession:
    token: str
    session: AuthSession


def is_setup_complete(session: Session) -> bool:
    return session.get(AuthCredential, SINGLETON_ID) is not None


def set_initial_password(session: Session, password: str, now: datetime) -> None:
    if is_setup_complete(session):
        raise AppError(403, "setup_completed", "Setup has already been completed.")
    session.add(
        AuthCredential(
            id=SINGLETON_ID, password_hash=hash_password(password), password_changed_at=now
        )
    )


def check_password(session: Session, password: str) -> bool:
    credential = session.get(AuthCredential, SINGLETON_ID)
    if credential is None:
        raise AppError(403, "setup_required", "Complete the first-run setup first.")
    return verify_password(credential.password_hash, password)


def change_password(
    session: Session, current: AuthSession, old: str, new: str, now: datetime
) -> None:
    credential = session.get(AuthCredential, SINGLETON_ID)
    assert credential is not None
    if not verify_password(credential.password_hash, old):
        raise _password_error(
            "current_password", "invalid_current_password", "Current password is incorrect."
        )
    if old == new:
        raise _password_error("new_password", "password_unchanged", "New password must differ.")

    credential.password_hash = hash_password(new)
    credential.password_changed_at = now
    session.execute(delete(AuthSession).where(AuthSession.id != current.id))


def create_session(
    session: Session, settings: Settings, now: datetime, user_agent: str | None, ip: str | None
) -> NewSession:
    token = new_token()
    auth_session = AuthSession(
        token_hash=hash_token(token),
        csrf_token=new_token(),
        created_at=now,
        last_seen_at=now,
        expires_at=now + timedelta(days=settings.session_absolute_days),
        user_agent=(user_agent or "")[:300] or None,
        ip_address=ip,
    )
    session.add(auth_session)
    session.flush()
    return NewSession(token=token, session=auth_session)


def find_active_session(
    session: Session, settings: Settings, token: str | None, now: datetime
) -> AuthSession | None:
    """Return the live session for a cookie token, deleting it if it has expired."""
    if not token:
        return None
    auth_session = session.scalar(
        select(AuthSession).where(AuthSession.token_hash == hash_token(token))
    )
    if auth_session is None:
        return None

    idle_limit = auth_session.last_seen_at + timedelta(days=settings.session_idle_days)
    if now >= auth_session.expires_at or now >= idle_limit:
        session.delete(auth_session)
        return None

    if now - auth_session.last_seen_at >= LAST_SEEN_RESOLUTION:
        auth_session.last_seen_at = now
    return auth_session


def _password_error(field: str, code: str, message: str) -> AppError:
    return AppError(
        422,
        "validation_error",
        "Request validation failed.",
        [{"field": field, "code": code, "message": message}],
    )
