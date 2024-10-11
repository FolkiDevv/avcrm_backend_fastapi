from typing import ClassVar
from uuid import UUID

from app.models.user import UserBase
from app.utils.partial import optional


class UserCreate(UserBase):
    is_active: ClassVar


@optional()
class UserUpdate(UserBase):
    pass


class UserRead(UserBase):
    id: UUID
    password: ClassVar
