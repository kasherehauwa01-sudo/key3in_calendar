from datetime import date
from pydantic import BaseModel, ConfigDict, Field

class RecurringEventWrite(BaseModel):
    text: str = Field(min_length=1, max_length=20000)
    start_date: date
    interval: int = Field(ge=1, le=999)
    unit: str = Field(pattern="^(day|week|month|year)$")
    weekdays: list[int] = Field(default_factory=list)
    end_date: date | None = None
    count: int | None = Field(default=None, ge=1, le=9999)

class RecurringEventRead(RecurringEventWrite):
    id: int
    user_id: int
    user_name: str
    user_color: str
    model_config = ConfigDict(from_attributes=True)
