from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request

from core.clock import Clock
from core.config import Settings
from core.db import UnitOfWork


def get_uow(request: Request) -> Iterator[UnitOfWork]:
    with UnitOfWork(request.app.state.session_factory) as uow:
        yield uow


def get_clock(request: Request) -> Clock:
    clock: Clock = request.app.state.clock
    return clock


def get_settings_dep(request: Request) -> Settings:
    settings: Settings = request.app.state.settings
    return settings


UowDep = Annotated[UnitOfWork, Depends(get_uow)]
ClockDep = Annotated[Clock, Depends(get_clock)]
SettingsDep = Annotated[Settings, Depends(get_settings_dep)]
