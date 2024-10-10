import uuid
from typing import ClassVar

from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from app.models.base import BaseIDModel, BaseUUIDModel
from app.models.role import Role


class UserBase(BaseUUIDModel):
    username: str = Field(nullable=False, unique=True)
    password: str

    first_name: str
    last_name: str
    email: EmailStr | None = Field(nullable=True, default=None)
    phone: PhoneNumber | None = Field(nullable=True, default=None)

    is_active: bool = Field(default=True, nullable=False)


class User(UserBase, table=True):
    roles: list["UserRoles"] | None = Relationship(
        # sa_relationship_kwargs={"lazy": "joined"}
    )


class UserPublic(UserBase):
    password: ClassVar[str]


class UserRoles(BaseIDModel, table=True):
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="unique_user_role"),)

    user_id: uuid.UUID = Field(foreign_key="user.id")
    role_id: uuid.UUID = Field(foreign_key="role.id")

    role: "Role" = Relationship()
