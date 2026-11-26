from fastapi import APIRouter, Request, Response, status
from sqlalchemy.exc import IntegrityError

from app_settings.service import get_app_settings, save_app_settings
from auth import service
from auth.deps import SESSION_COOKIE, SessionDep
from auth.schemas import AuthStatus, ChangePasswordRequest, LoginRequest, SessionInfo, SetupRequest
from auth.throttle import LoginThrottle
from core.config import Settings
from core.deps import ClockDep, SettingsDep, UowDep
from core.errors import AppError
from user_profile.service import create_profile

router = APIRouter(prefix="/auth", tags=["auth"])


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _set_cookie(
    response: Response, request: Request, settings: Settings, new: service.NewSession
) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        new.token,
        max_age=settings.session_absolute_days * 86400,
        httponly=True,
        samesite="lax",
        secure=settings.https_terminated or request.url.scheme == "https",
        path="/",
    )


@router.get("/status")
def auth_status(
    request: Request, uow: UowDep, clock: ClockDep, settings: SettingsDep
) -> AuthStatus:
    active = service.find_active_session(
        uow.session, settings, request.cookies.get(SESSION_COOKIE), clock.now()
    )
    uow.commit()
    return AuthStatus(
        setup_complete=service.is_setup_complete(uow.session), authenticated=active is not None
    )


@router.post("/setup", status_code=status.HTTP_201_CREATED)
def setup(
    body: SetupRequest,
    request: Request,
    response: Response,
    uow: UowDep,
    clock: ClockDep,
    settings: SettingsDep,
) -> SessionInfo:
    now = clock.now()
    service.set_initial_password(uow.session, body.password, now)
    create_profile(
        uow.session,
        body.profile.full_name,
        body.profile.citizenship_country_codes,
        body.profile.residence_country_code,
    )
    save_app_settings(
        uow.session, get_app_settings(uow.session).model_copy(update={"timezone": body.timezone})
    )
    new = service.create_session(
        uow.session, settings, now, request.headers.get("user-agent"), _client_ip(request)
    )
    try:
        uow.commit()
    except IntegrityError as exc:  # a concurrent setup won the singleton row
        raise AppError(403, "setup_completed", "Setup has already been completed.") from exc

    _set_cookie(response, request, settings, new)
    return SessionInfo(csrf_token=new.session.csrf_token, expires_at=new.session.expires_at)


@router.post("/login")
def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    uow: UowDep,
    clock: ClockDep,
    settings: SettingsDep,
) -> SessionInfo:
    throttle: LoginThrottle = request.app.state.login_throttle
    ip = _client_ip(request)
    throttle.check(ip)

    if not service.check_password(uow.session, body.password):
        throttle.record_failure(ip)
        raise AppError(401, "invalid_credentials", "Incorrect password.")

    throttle.reset(ip)
    new = service.create_session(
        uow.session, settings, clock.now(), request.headers.get("user-agent"), ip
    )
    uow.commit()
    _set_cookie(response, request, settings, new)
    return SessionInfo(csrf_token=new.session.csrf_token, expires_at=new.session.expires_at)


@router.get("/session")
def current_session(auth_session: SessionDep) -> SessionInfo:
    return SessionInfo(csrf_token=auth_session.csrf_token, expires_at=auth_session.expires_at)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(auth_session: SessionDep, response: Response, uow: UowDep) -> None:
    uow.session.delete(auth_session)
    uow.commit()
    response.delete_cookie(SESSION_COOKIE, path="/")


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    body: ChangePasswordRequest, auth_session: SessionDep, uow: UowDep, clock: ClockDep
) -> None:
    service.change_password(
        uow.session, auth_session, body.current_password, body.new_password, clock.now()
    )
    uow.commit()
