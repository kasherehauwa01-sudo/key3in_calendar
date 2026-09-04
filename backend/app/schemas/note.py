from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field

MAX_NOTE_LENGTH = 20_000

class NoteCreate(BaseModel):
    date: date
    text: str = Field(max_length=MAX_NOTE_LENGTH)

class NoteUpdate(BaseModel):
    text: str = Field(max_length=MAX_NOTE_LENGTH)

class NoteRead(BaseModel):
    id: int
    date: date
    text: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
