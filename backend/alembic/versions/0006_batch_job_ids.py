"""Unbounded job id lists: a deviation batch stores one PeriLab job id per sample (50 samples ~ 660 chars).

Revision ID: 0006_batch_job_ids
Revises: 0005_job_solver
Create Date: 2026-11-10

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006_batch_job_ids"
down_revision: Union[str, None] = "0005_job_solver"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("job_queue_entries") as batch:
        batch.alter_column("perilab_job_id", type_=sa.Text(), existing_type=sa.String(500), existing_nullable=True)
        batch.alter_column("job_ids", type_=sa.Text(), existing_type=sa.String(255), existing_nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("job_queue_entries") as batch:
        batch.alter_column("perilab_job_id", type_=sa.String(500), existing_type=sa.Text(), existing_nullable=True)
        batch.alter_column("job_ids", type_=sa.String(255), existing_type=sa.Text(), existing_nullable=False)
