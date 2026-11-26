"""Guards for the brief's hard rules (FR-061, C-09, NFR-021)."""

import ast
import json
from pathlib import Path

import pytest

from core.config import Settings, insecure_bind_error

BACKEND = Path(__file__).resolve().parents[2]
SKIP_DIRS = {"tests", "migrations", ".venv", "data"}
COUNTRY_CODES = {
    c["code"] for c in json.loads((BACKEND / "catalog/data/countries.json").read_text())
}


def _python_files() -> list[Path]:
    return [p for p in BACKEND.rglob("*.py") if not SKIP_DIRS & set(p.relative_to(BACKEND).parts)]


def test_no_country_codes_hardcoded_in_application_code() -> None:
    """Profile and country facts come from stored data only; code never names a country."""
    offenders = []
    for path in _python_files():
        for node in ast.walk(ast.parse(path.read_text(), str(path))):
            if isinstance(node, ast.Constant) and node.value in COUNTRY_CODES:
                offenders.append(f"{path.relative_to(BACKEND)}:{node.lineno} {node.value!r}")
    assert offenders == []


@pytest.mark.parametrize(
    ("host", "overrides", "allowed"),
    [
        ("127.0.0.1", {}, True),
        ("::1", {}, True),
        ("localhost", {}, True),
        ("0.0.0.0", {}, False),
        ("192.168.1.10", {"https_terminated": True}, True),
        ("0.0.0.0", {"allow_insecure_http": True}, True),
    ],
)
def test_insecure_bind_guard(host: str, overrides: dict[str, bool], allowed: bool) -> None:
    settings = Settings(host=host, _env_file=None, **overrides)  # type: ignore[arg-type]
    assert (insecure_bind_error(settings) is None) is allowed
