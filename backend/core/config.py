import ipaddress
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration, read from JOBORBIT_* environment variables or a .env file."""

    model_config = SettingsConfigDict(env_prefix="JOBORBIT_", env_file=".env", extra="ignore")

    host: str = "127.0.0.1"
    port: int = 8765
    data_dir: Path = Path("data")
    database_url: str = ""
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    static_dir: Path = Path(__file__).resolve().parents[2] / "frontend" / "dist"

    session_idle_days: int = 7
    session_absolute_days: int = 30
    # Set when a reverse proxy terminates HTTPS in front of the app (NFR-021).
    https_terminated: bool = False
    allow_insecure_http: bool = False

    @model_validator(mode="after")
    def _default_database_url(self) -> "Settings":
        if not self.database_url:
            self.database_url = f"sqlite:///{(self.data_dir / 'joborbit.db').resolve()}"
        return self


def insecure_bind_error(settings: Settings) -> str | None:
    """NFR-021: refuse plain HTTP on a non-loopback interface unless explicitly allowed."""
    try:
        loopback = ipaddress.ip_address(settings.host).is_loopback
    except ValueError:
        loopback = settings.host == "localhost"
    if loopback or settings.https_terminated or settings.allow_insecure_http:
        return None
    return (
        f"Refusing to listen on {settings.host} without HTTPS. Put a TLS reverse proxy in front "
        "and set JOBORBIT_HTTPS_TERMINATED=true, or set JOBORBIT_ALLOW_INSECURE_HTTP=true."
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
