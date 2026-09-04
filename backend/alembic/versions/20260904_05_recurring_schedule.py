"""add recurring event work/rest schedule"""
from alembic import op
import sqlalchemy as sa

revision = "20260904_05"
down_revision = "20260904_04"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("recurring_events", sa.Column("active_days", sa.Integer(), nullable=True))
    op.add_column("recurring_events", sa.Column("rest_days", sa.Integer(), nullable=True))

def downgrade():
    op.drop_column("recurring_events", "rest_days")
    op.drop_column("recurring_events", "active_days")
