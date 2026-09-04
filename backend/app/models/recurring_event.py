from datetime import date
from sqlalchemy import Date, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .note import Base

class RecurringEvent(Base):
    __tablename__ = "recurring_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    interval: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit: Mapped[str] = mapped_column(String(8), nullable=False)
    weekdays: Mapped[list[int]] = mapped_column(JSON, default=list, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date)
    count: Mapped[int | None] = mapped_column(Integer)
    user = relationship("User")

    @property
    def user_name(self) -> str:
        return self.user.name

    @property
    def user_color(self) -> str:
        return self.user.color
