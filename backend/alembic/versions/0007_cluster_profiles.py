"""Per-user Slurm cluster profiles (enterprise cluster jobs, ee/cluster.py).

Revision ID: 0007_cluster_profiles
Revises: 0006_batch_job_ids
Create Date: 2026-11-19

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007_cluster_profiles"
down_revision: Union[str, None] = "0006_batch_job_ids"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cluster_profiles",
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("host", sa.String(255), nullable=False),
        sa.Column("port", sa.Integer(), nullable=False, server_default="22"),
        sa.Column("username", sa.String(255), nullable=False),
        sa.Column("account", sa.String(255), nullable=False),
        sa.Column("perilab_path", sa.String(1000), nullable=False),
        sa.Column("workdir", sa.String(1000), nullable=False, server_default="~/perihub"),
        sa.Column("partition", sa.String(255), nullable=False, server_default=""),
        sa.Column("time_limit", sa.String(32), nullable=False, server_default="01:00:00"),
        sa.Column("job_template", sa.Text(), nullable=True),
        sa.Column("public_key", sa.Text(), nullable=True),
        sa.Column("private_key_enc", sa.Text(), nullable=True),
        sa.Column("host_key", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("cluster_profiles")
