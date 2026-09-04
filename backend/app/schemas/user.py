from pydantic import BaseModel, ConfigDict, Field, field_validator

class Credentials(BaseModel):
    login: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-zА-Яа-яЁё0-9_.-]+$")
    pin: str = Field(min_length=4, max_length=12, pattern=r"^[0-9]+$")

class RegisterRequest(Credentials):
    name: str = Field(min_length=1, max_length=80)

class UserUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    color: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        if not value.strip(): raise ValueError("Имя не может быть пустым")
        return value.strip()

class UserRead(BaseModel):
    id: int
    login: str
    name: str
    color: str
    model_config = ConfigDict(from_attributes=True)

class AuthResponse(BaseModel):
    token: str
    user: UserRead
