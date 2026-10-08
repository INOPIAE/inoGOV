import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def clean_name(value: str | None) -> str | None:
    return (value or "").strip() or None


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr
    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    roles: list[str] = ["user"]


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    active: bool | None = None
    blocked: bool | None = None
    roles: list[str] | None = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class UserInvite(BaseModel):
    email: EmailStr
    roles: list[str] = ["user"]


class ProfileUpdate(BaseModel):
    """Eigene Daten; der Benutzername ist bewusst nicht enthalten."""

    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = None
    current_password: str | None = None

    _clean = field_validator("first_name", "last_name", mode="before")(clean_name)


class OtpPassword(BaseModel):
    password: str
    otp: str | None = None


class OtpConfirm(BaseModel):
    setup_token: str
    code: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    email: str
    first_name: str | None
    last_name: str | None
    active: bool
    blocked: bool
    otp_enabled: bool
    pending: bool = False
    roles: list[str] = []
