"""create notes"""
from typing import Sequence
from alembic import op
import sqlalchemy as sa
revision: str = "20260904_01"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

def upgrade():
    op.create_table("notes", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("date", sa.Date(), nullable=False), sa.Column("text", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_notes_date", "notes", ["date"], unique=True)
def downgrade():
    op.drop_index("ix_notes_date", table_name="notes"); op.drop_table("notes")
