from typing import ClassVar
from uuid import UUID

from sqlmodel import Field

from app.models.user import UserBase
from app.utils.partial import optional


class UserCreate(UserBase):
    is_active: bool = Field(default=True, nullable=False)


@optional()
class UserUpdate(UserBase):
    pass


class UserRead(UserBase):
    id: UUID
    password: ClassVar
