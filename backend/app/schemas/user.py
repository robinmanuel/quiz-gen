from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = Field(default=None, min_length=1, max_length=50)
    current_password: str | None = None
    new_password: str | None = Field(default=None, min_length=8)


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_admin: bool


