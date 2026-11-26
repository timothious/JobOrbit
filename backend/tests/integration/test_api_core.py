import json
import logging
from typing import Annotated

import pytest
from fastapi import Query
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from core.config import Settings
from core.errors import AppError
from core.pagination import PageQuery


def test_health_reports_ok_with_request_id_and_security_headers(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["db"] == "ok"
    assert response.json()["setup_complete"] is False
    assert len(response.headers["X-Request-ID"]) == 32
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
    assert "Strict-Transport-Security" not in response.headers


def test_hsts_only_over_https(client: TestClient) -> None:
    response = client.get("https://testserver/api/v1/health")
    assert "Strict-Transport-Security" in response.headers


def test_unknown_route_uses_error_envelope(client: TestClient) -> None:
    response = client.get("/api/v1/nope")

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "not_found"
    assert body["request_id"] == response.headers["X-Request-ID"]


def test_validation_errors_list_field_details(client: TestClient) -> None:
    @client.app.get("/_test/items")  # type: ignore[attr-defined,untyped-decorator]
    def items(page: PageQuery, q: Annotated[str, Query(max_length=3)] = "") -> dict[str, int]:
        return {"page": page.page}

    response = client.get("/_test/items?page=0&q=toolong")

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert {d["field"] for d in error["details"]} == {"page", "q"}


def test_app_error_is_rendered_with_its_code_and_headers(client: TestClient) -> None:
    @client.app.get("/_test/limited")  # type: ignore[attr-defined,untyped-decorator]
    def limited() -> None:
        raise AppError(429, "rate_limited", "Slow down.", headers={"Retry-After": "30"})

    response = client.get("/_test/limited")

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "30"
    assert response.json()["error"] == {"code": "rate_limited", "message": "Slow down."}


def test_unhandled_error_returns_500_envelope_without_leaking_details(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    @client.app.get("/_test/boom")  # type: ignore[attr-defined,untyped-decorator]
    def boom() -> None:
        raise ValueError("secret internals")

    with caplog.at_level(logging.ERROR):
        response = client.get("/_test/boom")

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_error"
    assert "secret internals" not in response.text
    assert response.json()["request_id"] == response.headers["X-Request-ID"]
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert any(r.message == "unhandled_error" for r in caplog.records)


def test_health_returns_503_when_database_is_unreachable(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from sqlalchemy.orm import Session

    def fail(*_: object, **__: object) -> None:
        raise OperationalError("SELECT 1", {}, Exception("down"))

    monkeypatch.setattr(Session, "execute", fail)
    response = client.get("/api/v1/health")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "unavailable"


def test_log_file_is_written_as_json(client: TestClient, settings: Settings) -> None:
    client.get("/api/v1/health")
    for handler in logging.getLogger().handlers:
        handler.flush()

    lines = (settings.data_dir / "logs" / "joborbit.log").read_text().splitlines()
    entries = [json.loads(line) for line in lines]
    request_log = next(e for e in entries if e["event"] == "request")
    assert request_log["path"] == "/api/v1/health"
    assert request_log["status"] == 200
    assert request_log["request_id"]
