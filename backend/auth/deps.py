import secrets
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import APIKeyCookie, APIKeyHeader

from auth.models import AuthSession
from auth.service import find_active_session, is_setup_complete
from core.deps import ClockDep, SettingsDep, UowDep
from core.errors import AppError

SESSION_COOKIE = "jo_session"
CSRF_HEADER = "X-JobOrbit-CSRF"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

# Declared as security schemes so Swagger UI can send them ("Authorize" button).
session_cookie = APIKeyCookie(name=SESSION_COOKIE, auto_error=False)
csrf_header = APIKeyHeader(name=CSRF_HEADER, auto_error=False)


def require_session(
    request: Request,
    uow: UowDep,
    clock: ClockDep,
    settings: SettingsDep,
    token: Annotated[str | None, Depends(session_cookie)],
    csrf: Annotated[str | None, Depends(csrf_header)],
) -> AuthSession:
    """Authenticate the request by session cookie; non-GET requests also need the CSRF header."""
    auth_session = find_active_session(uow.session, settings, token, clock.now())
    uow.commit()  # persist last-seen updates and expired-session deletions
    if auth_session is None:
        raise AppError(401, "unauthenticated", "Sign in to continue.")

    csrf_ok = secrets.compare_digest(csrf or "", auth_session.csrf_token)
    if request.method not in SAFE_METHODS and not csrf_ok:
        raise AppError(403, "csrf_failed", "Missing or invalid CSRF token.")
    return auth_session


SessionDep = Annotated[AuthSession, Depends(require_session)]


def require_session_or_setup(
    request: Request,
    uow: UowDep,
    clock: ClockDep,
    settings: SettingsDep,
    token: Annotated[str | None, Depends(session_cookie)],
    csrf: Annotated[str | None, Depends(csrf_header)],
) -> None:
    """Public until first-run setup is complete (the setup form needs it), then like `require_session`."""
    if not is_setup_complete(uow.session):
        return
    require_session(request, uow, clock, settings, token, csrf)
