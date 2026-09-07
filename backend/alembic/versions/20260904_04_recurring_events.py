"""recurring events"""
from alembic import op
import sqlalchemy as sa
revision="20260904_04";down_revision="20260904_03";branch_labels=None;depends_on=None
def upgrade():
    op.create_table("recurring_events",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("user_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),sa.Column("text",sa.Text(),nullable=False),sa.Column("start_date",sa.Date(),nullable=False),sa.Column("interval",sa.Integer(),nullable=False),sa.Column("unit",sa.String(8),nullable=False),sa.Column("weekdays",sa.JSON(),nullable=False),sa.Column("end_date",sa.Date()),sa.Column("count",sa.Integer()))
def downgrade(): op.drop_table("recurring_events")
