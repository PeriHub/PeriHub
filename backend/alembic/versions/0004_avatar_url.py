"""Avatar URL from the IdP's picture claim.

Revision ID: 0004_avatar_url
Revises: 0003_job_notifications
Create Date: 2026-10-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004_avatar_url"
down_revision: Union[str, None] = "0003_job_notifications"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("avatar_url", sa.String(length=2000), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "avatar_url")
