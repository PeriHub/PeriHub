"""Account setting for job notification emails.

Revision ID: 0003_job_notifications
Revises: 0002_api_keys
Create Date: 2026-10-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_job_notifications"
down_revision: Union[str, None] = "0002_api_keys"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("notify_job_emails", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column("users", "notify_job_emails")
