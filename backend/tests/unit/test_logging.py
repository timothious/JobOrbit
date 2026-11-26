import json
import logging

from core.logging import JsonFormatter, request_id_var


def _record(msg: str, **extra: object) -> logging.LogRecord:
    record = logging.LogRecord("joborbit.test", logging.INFO, "", 0, msg, None, None)
    record.__dict__.update(extra)
    return record


def test_json_line_has_required_fields_and_extras() -> None:
    token = request_id_var.set("abc123")
    try:
        entry = json.loads(JsonFormatter().format(_record("sync_done", rows=5)))
    finally:
        request_id_var.reset(token)

    assert entry["level"] == "INFO"
    assert entry["module"] == "joborbit.test"
    assert entry["event"] == "sync_done"
    assert entry["request_id"] == "abc123"
    assert entry["rows"] == 5
    assert entry["ts"].endswith("+00:00")
