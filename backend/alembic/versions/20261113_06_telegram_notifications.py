"""Add opt-in Telegram links and a delivery queue."""
from alembic import op
import sqlalchemy as sa

revision = "20261113_06"
down_revision = "20260904_05"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "telegram_links",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("chat_id", sa.BigInteger(), nullable=False, unique=True),
    )
    op.create_table(
        "telegram_deliveries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recipient_id", sa.Integer(), sa.ForeignKey("telegram_links.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_telegram_deliveries_due", "telegram_deliveries", ["next_attempt_at", "id"])


def downgrade():
    op.drop_index("ix_telegram_deliveries_due", table_name="telegram_deliveries")
    op.drop_table("telegram_deliveries")
    op.drop_table("telegram_links")
