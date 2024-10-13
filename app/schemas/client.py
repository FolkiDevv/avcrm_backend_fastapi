from typing import ClassVar
from uuid import UUID

from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlmodel import Field

from app.models.client import ClientBase
from app.schemas.user import UserRead
from app.utils.partial import optional


class ClientBaseCU(ClientBase):
    first_name: str = Field(min_length=2, max_length=50, nullable=False)
    last_name: str = Field(min_length=2, max_length=50, nullable=False)
    email: EmailStr | None = Field(nullable=True, default=None)
    phone: PhoneNumber | None = Field(nullable=True, default=None)


class ClientCreate(ClientBaseCU):
    user_id: ClassVar


@optional()
class ClientUpdate(ClientBaseCU):
    pass


class ClientRead(ClientBase):
    id: UUID
    password: ClassVar
    user: UserRead
