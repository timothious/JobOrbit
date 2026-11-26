"""initial schema

Revision ID: 0eaf2f4c0507
Revises:
Create Date: 2026-11-26 12:28:31.137722

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0eaf2f4c0507"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "app_settings",
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column(
            "value",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("key", name=op.f("pk_app_settings")),
    )
    op.create_table(
        "auth_credentials",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("password_changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.CheckConstraint("id = 1", name=op.f("ck_auth_credentials_singleton")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_auth_credentials")),
    )
    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("csrf_token", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_agent", sa.String(length=300), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_auth_sessions")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_auth_sessions_token_hash")),
    )
    with op.batch_alter_table("auth_sessions", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_auth_sessions_expires_at"), ["expires_at"], unique=False
        )

    op.create_table(
        "countries",
        sa.Column("code", sa.String(length=2), nullable=False),
        sa.Column("iso3", sa.String(length=3), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("official_name", sa.String(length=200), nullable=True),
        sa.Column("region", sa.String(length=50), nullable=True),
        sa.Column("subregion", sa.String(length=80), nullable=True),
        sa.Column("currency_code", sa.String(length=3), nullable=True),
        sa.Column(
            "languages",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column("english_status", sa.String(length=30), nullable=False),
        sa.Column("english_status_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("demonym", sa.String(length=80), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "english_status IN ('official', 'widely_used_in_business', 'limited', 'unknown')",
            name=op.f("ck_countries_english_status"),
        ),
        sa.PrimaryKeyConstraint("code", name=op.f("pk_countries")),
        sa.UniqueConstraint("iso3", name=op.f("uq_countries_iso3")),
    )
    with op.batch_alter_table("countries", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_countries_name"), ["name"], unique=False)
        batch_op.create_index(batch_op.f("ix_countries_region"), ["region"], unique=False)

    op.create_table(
        "job_sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("adapter_type", sa.String(length=30), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column(
            "config",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column(
            "credential_env_keys",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column("fetch_interval_minutes", sa.Integer(), nullable=False),
        sa.Column("snapshot_mode", sa.String(length=12), nullable=False),
        sa.Column("stale_after_hours", sa.Integer(), nullable=False),
        sa.Column("expire_after_days", sa.Integer(), nullable=False),
        sa.Column("priority", sa.SmallInteger(), nullable=False),
        sa.Column(
            "coverage_countries",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column("coverage_note", sa.String(length=500), nullable=True),
        sa.Column("attribution_text", sa.String(length=200), nullable=True),
        sa.Column("attribution_url", sa.String(length=2048), nullable=True),
        sa.Column("terms_url", sa.String(length=2048), nullable=True),
        sa.Column("terms_reviewed_at", sa.Date(), nullable=True),
        sa.Column("requires_link_back", sa.Boolean(), nullable=False),
        sa.Column("health_status", sa.String(length=12), nullable=False),
        sa.Column("consecutive_failures", sa.Integer(), nullable=False),
        sa.Column("backoff_multiplier", sa.SmallInteger(), nullable=False),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "adapter_type IN ('remoteok', 'remotive', 'arbeitnow', 'adzuna', 'usajobs', 'greenhouse', 'lever', 'manual')",
            name=op.f("ck_job_sources_adapter_type"),
        ),
        sa.CheckConstraint(
            "health_status IN ('never_run', 'healthy', 'degraded', 'failing', 'auth_error', 'disabled')",
            name=op.f("ck_job_sources_health_status"),
        ),
        sa.CheckConstraint(
            "snapshot_mode IN ('full', 'incremental')", name=op.f("ck_job_sources_snapshot_mode")
        ),
        sa.CheckConstraint(
            "fetch_interval_minutes > 0", name=op.f("ck_job_sources_fetch_interval_positive")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_job_sources")),
        sa.UniqueConstraint("key", name=op.f("uq_job_sources_key")),
    )
    with op.batch_alter_table("job_sources", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_job_sources_next_run_at"), ["next_run_at"], unique=False
        )

    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("normalized_name", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=20), nullable=True),
        sa.Column(
            "aliases",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column("is_system", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "category IN ('programming_language', 'framework', 'library', 'tool', 'cloud', 'database', 'data', 'ml_ai', 'devops', 'soft', 'domain', 'other')",
            name=op.f("ck_skills_category"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_skills")),
        sa.UniqueConstraint("normalized_name", name=op.f("uq_skills_normalized_name")),
    )
    op.create_table(
        "region_members",
        sa.Column("region_code", sa.String(length=20), nullable=False),
        sa.Column("country_code", sa.String(length=2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["country_code"],
            ["countries.code"],
            name=op.f("fk_region_members_country_code_countries"),
        ),
        sa.PrimaryKeyConstraint("region_code", "country_code", name=op.f("pk_region_members")),
    )
    op.create_table(
        "sync_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("trigger", sa.String(length=10), nullable=False),
        sa.Column("status", sa.String(length=10), nullable=False),
        sa.Column("queued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("http_requests", sa.Integer(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("records_fetched", sa.Integer(), nullable=False),
        sa.Column("records_valid", sa.Integer(), nullable=False),
        sa.Column("records_invalid", sa.Integer(), nullable=False),
        sa.Column("jobs_created", sa.Integer(), nullable=False),
        sa.Column("jobs_updated", sa.Integer(), nullable=False),
        sa.Column("jobs_unchanged", sa.Integer(), nullable=False),
        sa.Column("duplicates_merged", sa.Integer(), nullable=False),
        sa.Column("jobs_marked_stale", sa.Integer(), nullable=False),
        sa.Column("jobs_expired", sa.Integer(), nullable=False),
        sa.Column("error_type", sa.String(length=20), nullable=True),
        sa.Column("error_message", sa.String(length=1000), nullable=True),
        sa.Column(
            "errors",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "error_type IN ('network', 'timeout', 'http', 'auth', 'not_found', 'rate_limited', 'schema', 'validation', 'interrupted', 'internal')",
            name=op.f("ck_sync_logs_error_type"),
        ),
        sa.CheckConstraint(
            "status IN ('queued', 'running', 'success', 'partial', 'failed', 'cancelled', 'skipped')",
            name=op.f("ck_sync_logs_status"),
        ),
        sa.CheckConstraint(
            "trigger IN ('scheduled', 'manual', 'retry', 'startup')",
            name=op.f("ck_sync_logs_trigger"),
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["job_sources.id"],
            name=op.f("fk_sync_logs_source_id_job_sources"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sync_logs")),
    )
    with op.batch_alter_table("sync_logs", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_sync_logs_status"), ["status"], unique=False)
        batch_op.create_index(
            "uq_sync_logs_source_id_active",
            ["source_id"],
            unique=True,
            sqlite_where=sa.text("status IN ('queued', 'running')"),
            postgresql_where=sa.text("status IN ('queued', 'running')"),
        )
    op.create_index("ix_sync_logs_source_id_queued_at", "sync_logs", ["source_id", "queued_at"])

    op.create_table(
        "user_profile",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=True),
        sa.Column("residence_country_code", sa.String(length=2), nullable=True),
        sa.Column("profile_version", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.CheckConstraint("id = 1", name=op.f("ck_user_profile_singleton")),
        sa.ForeignKeyConstraint(
            ["residence_country_code"],
            ["countries.code"],
            name=op.f("fk_user_profile_residence_country_code_countries"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_profile")),
    )
    op.create_table(
        "profile_citizenships",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=False),
        sa.Column("country_code", sa.String(length=2), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["country_code"],
            ["countries.code"],
            name=op.f("fk_profile_citizenships_country_code_countries"),
        ),
        sa.ForeignKeyConstraint(
            ["profile_id"],
            ["user_profile.id"],
            name=op.f("fk_profile_citizenships_profile_id_user_profile"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_profile_citizenships")),
        sa.UniqueConstraint(
            "profile_id", "country_code", name=op.f("uq_profile_citizenships_profile_id")
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("profile_citizenships")
    op.drop_table("user_profile")
    op.drop_index("ix_sync_logs_source_id_queued_at", table_name="sync_logs")
    with op.batch_alter_table("sync_logs", schema=None) as batch_op:
        batch_op.drop_index(
            "uq_sync_logs_source_id_active",
            sqlite_where=sa.text("status IN ('queued', 'running')"),
            postgresql_where=sa.text("status IN ('queued', 'running')"),
        )
        batch_op.drop_index(batch_op.f("ix_sync_logs_status"))

    op.drop_table("sync_logs")
    op.drop_table("region_members")
    op.drop_table("skills")
    with op.batch_alter_table("job_sources", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_job_sources_next_run_at"))

    op.drop_table("job_sources")
    with op.batch_alter_table("countries", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_countries_region"))
        batch_op.drop_index(batch_op.f("ix_countries_name"))

    op.drop_table("countries")
    with op.batch_alter_table("auth_sessions", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_auth_sessions_expires_at"))

    op.drop_table("auth_sessions")
    op.drop_table("auth_credentials")
    op.drop_table("app_settings")
