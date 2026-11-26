from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from auth.throttle import LoginThrottle
from core.config import Settings
from main_api import create_app

PASSWORD = "correct horse battery"


class FakeClock:
    def __init__(self) -> None:
        self.current = datetime(2026, 11, 26, 9, 0, tzinfo=UTC)

    def now(self) -> datetime:
        return self.current

    def advance(self, **kwargs: float) -> None:
        self.current += timedelta(**kwargs)


def make_client(settings: Settings, clock: FakeClock) -> TestClient:
    app = create_app(settings, clock=clock)
    app.state.login_throttle = LoginThrottle(clock, delay_step_seconds=0)
    return TestClient(app)


def complete_setup(client: TestClient, **overrides: object) -> str:
    body = {
        "password": PASSWORD,
        "profile": {
            "full_name": "Test User",
            "citizenship_country_codes": ["PK"],
            "residence_country_code": "PK",
        },
        "timezone": "Asia/Karachi",
        **overrides,
    }
    response = client.post("/api/v1/auth/setup", json=body)
    assert response.status_code == 201, response.text
    csrf: str = response.json()["csrf_token"]
    client.headers["X-JobOrbit-CSRF"] = csrf
    return csrf
