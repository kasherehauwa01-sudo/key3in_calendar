"""add notification read state"""
from typing import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260904_03"
down_revision: str | None = "20260904_02"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade():
    op.create_table(
        "notification_reads",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("note_id", sa.Integer(), sa.ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("read_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade():
    op.drop_table("notification_reads")
