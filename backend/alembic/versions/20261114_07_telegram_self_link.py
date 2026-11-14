"""Add expiring Telegram account link requests."""
from alembic import op
import sqlalchemy as sa

revision = "20261114_07"
down_revision = "20261113_06"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "telegram_link_requests",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("token_hash", sa.String(64), unique=True, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table("telegram_link_requests")
