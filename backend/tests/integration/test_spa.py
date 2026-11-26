from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from core.config import Settings
from tests.helpers import FakeClock, make_client


@pytest.fixture
def spa_client(settings: Settings, clock: FakeClock, tmp_path: Path) -> Iterator[TestClient]:
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("<html>app</html>")
    (dist / "assets" / "app.js").write_text("console.log(1)")
    (dist / "manifest.webmanifest").write_text("{}")
    (tmp_path / "secret.txt").write_text("secret")
    with make_client(settings.model_copy(update={"static_dir": dist}), clock) as client:
        yield client


def test_serves_index_and_client_routes(spa_client: TestClient) -> None:
    for path in ("/", "/jobs/42", "/settings?tab=sources"):
        response = spa_client.get(path)
        assert response.status_code == 200
        assert response.text == "<html>app</html>"
    assert spa_client.get("/").headers["cache-control"] == "no-cache"


def test_serves_static_files(spa_client: TestClient) -> None:
    assert spa_client.get("/assets/app.js").text == "console.log(1)"
    manifest = spa_client.get("/manifest.webmanifest")
    assert manifest.text == "{}"
    assert manifest.headers["cache-control"] == "no-cache"


def test_does_not_escape_the_static_dir(spa_client: TestClient) -> None:
    response = spa_client.get("/%2E%2E/secret.txt")
    assert "secret" not in response.text


def test_unknown_api_paths_stay_json_404(spa_client: TestClient) -> None:
    response = spa_client.get("/api/v1/nope")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_swagger_docs_get_their_own_csp(spa_client: TestClient) -> None:
    docs = spa_client.get("/docs")
    assert docs.status_code == 200
    assert "cdn.jsdelivr.net" in docs.headers["Content-Security-Policy"]
    assert "cdn.jsdelivr.net" not in spa_client.get("/").headers["Content-Security-Policy"]
