from datetime import date, datetime
from typing import Any

from sqlalchemy import CheckConstraint, ForeignKey, Index, SmallInteger, String, text
from sqlalchemy.orm import Mapped, mapped_column

from core.base import Base, TimestampMixin, check_in

ADAPTER_TYPES = (
    "remoteok", "remotive", "arbeitnow", "adzuna", "usajobs", "greenhouse", "lever", "manual",
)  # fmt: skip
SOURCE_HEALTH = ("never_run", "healthy", "degraded", "failing", "auth_error", "disabled")
SYNC_TRIGGERS = ("scheduled", "manual", "retry", "startup")
SYNC_STATUSES = ("queued", "running", "success", "partial", "failed", "cancelled", "skipped")
SYNC_ERROR_TYPES = (
    "network", "timeout", "http", "auth", "not_found", "rate_limited",
    "schema", "validation", "interrupted", "internal",
)  # fmt: skip


class JobSource(TimestampMixin, Base):
    __tablename__ = "job_sources"
    __table_args__ = (
        check_in("adapter_type", ADAPTER_TYPES),
        check_in("snapshot_mode", ("full", "incremental")),
        check_in("health_status", SOURCE_HEALTH),
        CheckConstraint("fetch_interval_minutes > 0", name="fetch_interval_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(100), unique=True)
    adapter_type: Mapped[str] = mapped_column(String(30))
    display_name: Mapped[str] = mapped_column(String(100))
    enabled: Mapped[bool] = mapped_column(default=False)
    config: Mapped[dict[str, Any]] = mapped_column(default=dict)
    credential_env_keys: Mapped[list[Any]] = mapped_column(default=list)
    fetch_interval_minutes: Mapped[int]
    snapshot_mode: Mapped[str] = mapped_column(String(12))
    stale_after_hours: Mapped[int] = mapped_column(default=72)
    expire_after_days: Mapped[int]
    priority: Mapped[int] = mapped_column(SmallInteger)
    coverage_countries: Mapped[list[Any]] = mapped_column(default=list)
    coverage_note: Mapped[str | None] = mapped_column(String(500))
    attribution_text: Mapped[str | None] = mapped_column(String(200))
    attribution_url: Mapped[str | None] = mapped_column(String(2048))
    terms_url: Mapped[str | None] = mapped_column(String(2048))
    terms_reviewed_at: Mapped[date | None]
    requires_link_back: Mapped[bool] = mapped_column(default=True)
    health_status: Mapped[str] = mapped_column(String(12), default="never_run")
    consecutive_failures: Mapped[int] = mapped_column(default=0)
    backoff_multiplier: Mapped[int] = mapped_column(SmallInteger, default=1)
    last_run_at: Mapped[datetime | None]
    last_success_at: Mapped[datetime | None]
    next_run_at: Mapped[datetime | None] = mapped_column(index=True)


class SyncLog(TimestampMixin, Base):
    __tablename__ = "sync_logs"
    __table_args__ = (
        check_in("trigger", SYNC_TRIGGERS),
        check_in("status", SYNC_STATUSES),
        check_in("error_type", SYNC_ERROR_TYPES),
        Index("ix_sync_logs_source_id_queued_at", "source_id", "queued_at"),
        # At most one queued/running run per source (no overlapping syncs).
        Index(
            "uq_sync_logs_source_id_active",
            "source_id",
            unique=True,
            sqlite_where=text("status IN ('queued', 'running')"),
            postgresql_where=text("status IN ('queued', 'running')"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("job_sources.id", ondelete="CASCADE"))
    trigger: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(10), index=True)
    queued_at: Mapped[datetime]
    started_at: Mapped[datetime | None]
    finished_at: Mapped[datetime | None]
    duration_ms: Mapped[int | None]
    http_requests: Mapped[int] = mapped_column(default=0)
    attempts: Mapped[int] = mapped_column(default=0)
    records_fetched: Mapped[int] = mapped_column(default=0)
    records_valid: Mapped[int] = mapped_column(default=0)
    records_invalid: Mapped[int] = mapped_column(default=0)
    jobs_created: Mapped[int] = mapped_column(default=0)
    jobs_updated: Mapped[int] = mapped_column(default=0)
    jobs_unchanged: Mapped[int] = mapped_column(default=0)
    duplicates_merged: Mapped[int] = mapped_column(default=0)
    jobs_marked_stale: Mapped[int] = mapped_column(default=0)
    jobs_expired: Mapped[int] = mapped_column(default=0)
    error_type: Mapped[str | None] = mapped_column(String(20))
    error_message: Mapped[str | None] = mapped_column(String(1000))
    errors: Mapped[list[Any]] = mapped_column(default=list)
