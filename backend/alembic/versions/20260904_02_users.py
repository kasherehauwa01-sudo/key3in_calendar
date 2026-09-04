"""add users, sessions and per-user notes"""
from typing import Sequence
from alembic import op
import sqlalchemy as sa
revision: str = "20260904_02"
down_revision: str | None = "20260904_01"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

def upgrade():
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("login", sa.String(50), nullable=False), sa.Column("name", sa.String(80), nullable=False), sa.Column("pin_hash", sa.String(256), nullable=False), sa.Column("color", sa.String(7), server_default="#425f91", nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_users_login", "users", ["login"], unique=True)
    op.create_table("sessions", sa.Column("token", sa.String(64), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"])
    op.add_column("notes", sa.Column("user_id", sa.Integer(), nullable=True))
    # Ранее созданные однопользовательские заметки сохраняются за служебным пользователем.
    op.execute("INSERT INTO users (login, name, pin_hash, color) VALUES ('legacy', 'Пользователь', 'migration:no-login', '#425f91')")
    op.execute("UPDATE notes SET user_id = (SELECT id FROM users WHERE login = 'legacy')")
    op.alter_column("notes", "user_id", nullable=False)
    op.create_foreign_key("fk_notes_user_id", "notes", "users", ["user_id"], ["id"], ondelete="CASCADE")
    op.drop_index("ix_notes_date", table_name="notes")
    op.create_index("ix_notes_date", "notes", ["date"], unique=False)
    op.create_unique_constraint("uq_notes_date_user", "notes", ["date", "user_id"])

def downgrade():
    op.drop_constraint("uq_notes_date_user", "notes", type_="unique")
    op.drop_constraint("fk_notes_user_id", "notes", type_="foreignkey")
    op.drop_column("notes", "user_id")
    op.drop_index("ix_notes_date", table_name="notes")
    op.create_index("ix_notes_date", "notes", ["date"], unique=True)
    op.drop_index("ix_sessions_user_id", table_name="sessions")
    op.drop_table("sessions")
    op.drop_index("ix_users_login", table_name="users")
    op.drop_table("users")
