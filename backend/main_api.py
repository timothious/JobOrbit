import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from importlib.metadata import version

import uvicorn
from fastapi import APIRouter, Depends, FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from app_settings.api import router as settings_router
from auth.api import router as auth_router
from auth.deps import require_session, require_session_or_setup
from auth.service import is_setup_complete
from auth.throttle import LoginThrottle
from catalog.api import options_router as country_options_router
from catalog.api import router as countries_router
from core.clock import Clock, SystemClock
from core.config import Settings, get_settings, insecure_bind_error
from core.db import create_db_engine
from core.deps import UowDep
from core.errors import error_response, register_exception_handlers
from core.logging import configure_logging
from core.middleware import RequestContextMiddleware, SecurityHeadersMiddleware
from core.spa import mount_spa
from user_profile.api import router as profile_router

__version__ = version("joborbit")

system_router = APIRouter(tags=["system"])


@system_router.get("/health")
def health(uow: UowDep) -> JSONResponse:
    try:
        uow.session.execute(text("SELECT 1"))
        setup_complete = is_setup_complete(uow.session)
    except SQLAlchemyError:
        return error_response(503, "unavailable", "Database is unreachable.")
    return JSONResponse(
        {"status": "ok", "version": __version__, "db": "ok", "setup_complete": setup_complete}
    )


def create_app(settings: Settings | None = None, clock: Clock | None = None) -> FastAPI:
    settings = settings or get_settings()
    clock = clock or SystemClock()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        configure_logging(settings.log_level, settings.data_dir / "logs")
        engine = create_db_engine(settings.database_url)
        app.state.session_factory = sessionmaker(engine, expire_on_commit=False)
        yield
        engine.dispose()

    app = FastAPI(title="JobOrbit", version=__version__, lifespan=lifespan, redoc_url=None)
    app.state.settings = settings
    app.state.clock = clock
    app.state.login_throttle = LoginThrottle(clock)

    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    register_exception_handlers(app)

    protected = [Depends(require_session)]
    api = APIRouter(prefix="/api/v1")
    api.include_router(system_router)
    api.include_router(auth_router)
    api.include_router(settings_router, dependencies=protected)
    api.include_router(profile_router, dependencies=protected)
    api.include_router(country_options_router, dependencies=[Depends(require_session_or_setup)])
    api.include_router(countries_router, dependencies=protected)
    app.include_router(api)

    mount_spa(app, settings.static_dir)
    return app


def serve(settings: Settings, reload: bool = False) -> None:
    error = insecure_bind_error(settings)
    if error:
        sys.exit(error)
    uvicorn.run(
        "main_api:create_app",
        factory=True,
        host=settings.host,
        port=settings.port,
        reload=reload,
        proxy_headers=settings.https_terminated,
    )


def main() -> None:
    serve(get_settings())
