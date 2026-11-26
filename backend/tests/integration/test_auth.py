import pytest
from fastapi.testclient import TestClient

from core.config import Settings
from tests.helpers import PASSWORD, FakeClock, complete_setup, make_client

STATUS = "/api/v1/auth/status"


def test_status_before_and_after_setup(client: TestClient) -> None:
    assert client.get(STATUS).json() == {"setup_complete": False, "authenticated": False}
    complete_setup(client)
    assert client.get(STATUS).json() == {"setup_complete": True, "authenticated": True}


def test_setup_creates_profile_and_settings(authed: TestClient) -> None:
    profile = authed.get("/api/v1/profile").json()
    assert profile["full_name"] == "Test User"
    assert profile["citizenships"] == [{"country_code": "PK", "is_primary": True}]
    assert profile["residence_country_code"] == "PK"
    assert authed.get("/api/v1/settings").json()["timezone"] == "Asia/Karachi"


def test_setup_sets_a_hardened_session_cookie(client: TestClient) -> None:
    response = client.post("/api/v1/auth/setup", json={"password": PASSWORD})
    cookie = response.headers["set-cookie"].lower()
    assert "jo_session=" in cookie
    assert "httponly" in cookie
    assert "samesite=lax" in cookie
    assert "secure" not in cookie


def test_cookie_is_secure_over_https(settings: Settings, clock: FakeClock) -> None:
    with make_client(settings, clock) as client:
        response = client.post("https://testserver/api/v1/auth/setup", json={"password": PASSWORD})
    assert "secure" in response.headers["set-cookie"].lower()


def test_setup_only_once(authed: TestClient) -> None:
    response = authed.post("/api/v1/auth/setup", json={"password": PASSWORD})
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "setup_completed"


@pytest.mark.parametrize(
    ("body", "field"),
    [
        ({"password": "short"}, "password"),  # 5 characters, below the minimum of 6
        ({"password": " " * 6}, "password"),
        ({"password": PASSWORD, "timezone": "Mars/Base"}, "timezone"),
        (
            {"password": PASSWORD, "profile": {"citizenship_country_codes": ["pk"]}},
            "profile.citizenship_country_codes.0",
        ),
    ],
)
def test_setup_validation(client: TestClient, body: dict[str, object], field: str) -> None:
    response = client.post("/api/v1/auth/setup", json=body)
    assert response.status_code == 422
    assert field in {d["field"] for d in response.json()["error"]["details"]}


def test_setup_rejects_unknown_country_and_stays_incomplete(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/setup",
        json={"password": PASSWORD, "profile": {"residence_country_code": "ZZ"}},
    )
    assert response.status_code == 422
    assert response.json()["error"]["details"][0]["code"] == "unknown_country"
    assert client.get(STATUS).json()["setup_complete"] is False


def test_six_character_password_is_accepted(client: TestClient) -> None:
    assert client.post("/api/v1/auth/setup", json={"password": "abc123"}).status_code == 201


def test_login_requires_setup(client: TestClient) -> None:
    response = client.post("/api/v1/auth/login", json={"password": PASSWORD})
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "setup_required"


def test_login_success_and_failure(authed: TestClient) -> None:
    authed.cookies.clear()
    wrong = authed.post("/api/v1/auth/login", json={"password": "wrong password!!"})
    assert wrong.status_code == 401
    assert wrong.json()["error"]["code"] == "invalid_credentials"

    ok = authed.post("/api/v1/auth/login", json={"password": PASSWORD})
    assert ok.status_code == 200
    authed.headers["X-JobOrbit-CSRF"] = ok.json()["csrf_token"]
    assert authed.get("/api/v1/settings").status_code == 200


def test_login_is_throttled_after_five_failures(authed: TestClient, clock: FakeClock) -> None:
    for _ in range(5):
        assert (
            authed.post("/api/v1/auth/login", json={"password": "nope nope nope"}).status_code
            == 401
        )

    blocked = authed.post("/api/v1/auth/login", json={"password": PASSWORD})
    assert blocked.status_code == 429
    assert blocked.json()["error"]["code"] == "rate_limited"
    assert int(blocked.headers["Retry-After"]) == 15 * 60

    clock.advance(minutes=15, seconds=1)
    assert authed.post("/api/v1/auth/login", json={"password": PASSWORD}).status_code == 200


def test_protected_endpoints_require_a_session(client: TestClient) -> None:
    for path in (
        "/api/v1/settings",
        "/api/v1/profile",
        "/api/v1/countries",
        "/api/v1/auth/session",
    ):
        response = client.get(path)
        assert response.status_code == 401, path
        assert response.json()["error"]["code"] == "unauthenticated"


def test_state_changes_require_the_csrf_header(authed: TestClient) -> None:
    csrf = authed.headers.pop("X-JobOrbit-CSRF")
    settings = authed.get("/api/v1/settings").json()

    missing = authed.put("/api/v1/settings", json=settings)
    assert missing.status_code == 403
    assert missing.json()["error"]["code"] == "csrf_failed"
    wrong = authed.put("/api/v1/settings", json=settings, headers={"X-JobOrbit-CSRF": "x" * 43})
    assert wrong.status_code == 403
    assert (
        authed.put("/api/v1/settings", json=settings, headers={"X-JobOrbit-CSRF": csrf}).status_code
        == 200
    )


def test_session_endpoint_returns_the_csrf_token(authed: TestClient) -> None:
    body = authed.get("/api/v1/auth/session").json()
    assert body["csrf_token"] == authed.headers["X-JobOrbit-CSRF"]
    assert body["expires_at"] == "2026-12-26T09:00:00Z"


def test_idle_session_expires(authed: TestClient, clock: FakeClock) -> None:
    clock.advance(days=6, hours=23)
    assert authed.get("/api/v1/auth/session").status_code == 200  # activity resets idle timer
    clock.advance(days=7)
    assert authed.get("/api/v1/auth/session").status_code == 401


def test_absolute_session_lifetime(authed: TestClient, clock: FakeClock) -> None:
    for _ in range(5):  # active every 5-6 days, up to day 29
        clock.advance(days=6 if _ < 4 else 5)
        assert authed.get("/api/v1/auth/session").status_code == 200
    clock.advance(days=1)  # day 30 after login: expired despite regular activity
    assert authed.get("/api/v1/auth/session").status_code == 401


def test_logout_ends_the_session(authed: TestClient) -> None:
    session_cookie = authed.cookies["jo_session"]
    assert authed.post("/api/v1/auth/logout").status_code == 204
    authed.cookies.set("jo_session", session_cookie)  # replaying the old cookie must fail
    assert authed.get("/api/v1/auth/session").status_code == 401


def test_change_password(authed: TestClient, settings: Settings, clock: FakeClock) -> None:
    with make_client(settings, clock) as other:
        assert other.post("/api/v1/auth/login", json={"password": PASSWORD}).status_code == 200

        wrong = authed.post(
            "/api/v1/auth/change-password",
            json={"current_password": "not it at all", "new_password": "another long password"},
        )
        assert wrong.status_code == 422
        assert wrong.json()["error"]["details"][0]["code"] == "invalid_current_password"

        same = authed.post(
            "/api/v1/auth/change-password",
            json={"current_password": PASSWORD, "new_password": PASSWORD},
        )
        assert same.json()["error"]["details"][0]["code"] == "password_unchanged"

        ok = authed.post(
            "/api/v1/auth/change-password",
            json={"current_password": PASSWORD, "new_password": "another long password"},
        )
        assert ok.status_code == 204
        assert authed.get("/api/v1/auth/session").status_code == 200  # current session kept
        assert other.get("/api/v1/auth/session").status_code == 401  # other sessions revoked

    authed.cookies.clear()
    assert authed.post("/api/v1/auth/login", json={"password": PASSWORD}).status_code == 401
    assert (
        authed.post("/api/v1/auth/login", json={"password": "another long password"}).status_code
        == 200
    )
