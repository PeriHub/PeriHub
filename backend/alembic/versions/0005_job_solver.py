"""Per-run solver choice (local or external PeriLab API).

Revision ID: 0005_job_solver
Revises: 0004_avatar_url
Create Date: 2026-11-10

"""

import os
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005_job_solver"
down_revision: Union[str, None] = "0004_avatar_url"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "job_queue_entries",
        sa.Column("solver", sa.String(length=16), nullable=False, server_default="local"),
    )
    # Runs so far all went to whatever SOLVER_BACKEND pointed at.
    if os.getenv("SOLVER_BACKEND") == "external":
        op.execute("UPDATE job_queue_entries SET solver = 'external'")


def downgrade() -> None:
    op.drop_column("job_queue_entries", "solver")
