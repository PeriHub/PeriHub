# SPDX-License-Identifier: Apache-2.0
"""Initial schema: organizations, users, oauth_identities, admin_settings,
model_configs, materials, teams, projects, team/project memberships,
job_queue_entries.

Squashed from the original phase0-3 migrations (users/orgs, model
configs/materials, teams/projects, job queue) plus the PeriLab-API job
tracking columns on job_queue_entries, since no database had been created
against the unsquashed history yet - there's nothing to migrate *from*,
so one revision building the whole schema is simpler to read and run than
a chain of five.

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Phase 0: organizations, users, oauth_identities, admin_settings ---
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("plan", sa.String(length=32), nullable=False, server_default="community"),
        sa.Column("licensed_seats", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(length=36),
            sa.ForeignKey("organizations.id"),
            nullable=True,
        ),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column(
            "auth_provider",
            sa.String(length=32),
            nullable=False,
            server_default="local",
        ),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="member"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_org_id", "users", ["org_id"])

    op.create_table(
        "oauth_identities",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("provider_subject", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("provider", "provider_subject", name="uq_oauth_provider_subject"),
    )
    op.create_index("ix_oauth_identities_user_id", "oauth_identities", ["user_id"])

    op.create_table(
        "admin_settings",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(length=36),
            sa.ForeignKey("organizations.id"),
            nullable=True,
        ),
        sa.Column("key", sa.String(length=255), nullable=False),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("key", "org_id", name="uq_admin_settings_key_org"),
    )

    # --- Phase 1: model_configs, materials ---
    op.create_table(
        "model_configs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("owner_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "org_id",
            sa.String(length=36),
            sa.ForeignKey("organizations.id"),
            nullable=True,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("visibility", sa.String(length=16), nullable=False, server_default="private"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_model_configs_owner_id", "model_configs", ["owner_id"])
    op.create_index("ix_model_configs_org_id", "model_configs", ["org_id"])

    op.create_table(
        "materials",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("owner_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "org_id",
            sa.String(length=36),
            sa.ForeignKey("organizations.id"),
            nullable=True,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("properties", sa.JSON(), nullable=False),
        sa.Column("visibility", sa.String(length=16), nullable=False, server_default="private"),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_materials_owner_id", "materials", ["owner_id"])
    op.create_index("ix_materials_org_id", "materials", ["org_id"])

    # --- Phase 2: teams, projects, team/project scoping + tags on shared resources ---
    op.create_table(
        "teams",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(length=36),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_teams_org_id", "teams", ["org_id"])

    op.create_table(
        "team_memberships",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("team_id", sa.String(length=36), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("team_id", "user_id", name="uq_team_memberships_team_user"),
    )

    op.create_table(
        "projects",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(length=36),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column(
            "created_by",
            sa.String(length=36),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_projects_org_id", "projects", ["org_id"])

    op.create_table(
        "project_memberships",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "project_id",
            sa.String(length=36),
            sa.ForeignKey("projects.id"),
            nullable=False,
        ),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="member"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("project_id", "user_id", name="uq_project_memberships_project_user"),
    )

    for table in ("model_configs", "materials"):
        op.add_column(
            table,
            sa.Column(
                "team_id",
                sa.String(length=36),
                sa.ForeignKey("teams.id"),
                nullable=True,
            ),
        )
        op.add_column(
            table,
            sa.Column(
                "project_id",
                sa.String(length=36),
                sa.ForeignKey("projects.id"),
                nullable=True,
            ),
        )
        op.add_column(table, sa.Column("tags", sa.JSON(), nullable=False, server_default="[]"))
        op.create_index(f"ix_{table}_team_id", table, ["team_id"])
        op.create_index(f"ix_{table}_project_id", table, ["project_id"])

    # --- Phase 3: job_queue_entries (fair-share compute queue) ---
    op.create_table(
        "job_queue_entries",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "org_id",
            sa.String(length=36),
            sa.ForeignKey("organizations.id"),
            nullable=True,
        ),
        sa.Column(
            "project_id",
            sa.String(length=36),
            sa.ForeignKey("projects.id"),
            nullable=True,
        ),
        sa.Column("model_name", sa.String(length=255), nullable=False),
        sa.Column("model_folder_name", sa.String(length=255), nullable=False),
        sa.Column("remotepath", sa.String(length=1000), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="queued"),
        sa.Column("priority", sa.String(length=16), nullable=False, server_default="standard"),
        sa.Column("node_count", sa.Integer(), nullable=True),
        # The PeriLab API's own job id(s) (support/perilab_api_client.py),
        # set once support/solver_backend.py's submit() actually starts the
        # job - None while still queued. A comma-separated list when one
        # PeriHub submission fans out into several PeriLab jobs (see
        # PeriLabSolverBackend.submit's job_ids handling). This is what
        # status/log/cancel calls use to talk to the PeriLab API - there is
        # no more pid.txt/filesystem fallback for local (non-cluster) jobs.
        sa.Column("perilab_job_id", sa.String(length=500), nullable=True),
        # Solver options captured at submit time (support/writer/sbatch_writer.py
        # used to bake these into the runPerilab.sh script that was written to
        # disk *before* enqueueing, so a later dequeue just executed it without
        # needing them again - now that submission goes through the PeriLab API
        # instead of a pre-written script, try_run_next() needs them at dequeue
        # time, which can be well after the original request).
        sa.Column("solver_args", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("num_procs", sa.Integer(), nullable=False, server_default="1"),
        # "-1" for a single submission, or comma-separated PeriLab-side
        # variant ids for a batch of "<model>_<id>.yaml" files - see
        # PeriLabSolverBackend.submit.
        sa.Column("job_ids", sa.String(length=255), nullable=False, server_default="-1"),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error", sa.String(length=1000), nullable=True),
    )
    op.create_index("ix_job_queue_entries_user_id", "job_queue_entries", ["user_id"])
    op.create_index("ix_job_queue_entries_org_id", "job_queue_entries", ["org_id"])
    op.create_index("ix_job_queue_entries_status", "job_queue_entries", ["status"])


def downgrade() -> None:
    op.drop_index("ix_job_queue_entries_status", table_name="job_queue_entries")
    op.drop_index("ix_job_queue_entries_org_id", table_name="job_queue_entries")
    op.drop_index("ix_job_queue_entries_user_id", table_name="job_queue_entries")
    op.drop_table("job_queue_entries")

    for table in ("model_configs", "materials"):
        op.drop_index(f"ix_{table}_project_id", table_name=table)
        op.drop_index(f"ix_{table}_team_id", table_name=table)
        op.drop_column(table, "tags")
        op.drop_column(table, "project_id")
        op.drop_column(table, "team_id")

    op.drop_table("project_memberships")
    op.drop_index("ix_projects_org_id", table_name="projects")
    op.drop_table("projects")
    op.drop_table("team_memberships")
    op.drop_index("ix_teams_org_id", table_name="teams")
    op.drop_table("teams")

    op.drop_index("ix_materials_org_id", table_name="materials")
    op.drop_index("ix_materials_owner_id", table_name="materials")
    op.drop_table("materials")
    op.drop_index("ix_model_configs_org_id", table_name="model_configs")
    op.drop_index("ix_model_configs_owner_id", table_name="model_configs")
    op.drop_table("model_configs")

    op.drop_table("admin_settings")
    op.drop_index("ix_oauth_identities_user_id", table_name="oauth_identities")
    op.drop_table("oauth_identities")
    op.drop_index("ix_users_org_id", table_name="users")
    op.drop_table("users")
    op.drop_table("organizations")
