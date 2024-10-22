import uuid
from typing import TYPE_CHECKING

from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseIDModel, BaseUUIDModel
from app.models.user_login import UserLogin

if TYPE_CHECKING:
    from app.models.role import Role

PhoneNumber.phone_format = "E164"


class UserBase(SQLModel):
    username: str = Field(
        nullable=False,
        unique=True,
        schema_extra={"pattern": r"^[a-z0-9_]+$"},
    )
    password: str | None = Field(nullable=True)

    first_name: str = Field(min_length=2, max_length=50, nullable=False)
    last_name: str | None = Field(
        min_length=2, max_length=50, nullable=True, default=None
    )
    email: EmailStr | None = Field(nullable=True, default=None)
    phone: PhoneNumber | None = Field(nullable=True, default=None)

    is_active: bool = Field(default=True, nullable=False)


class User(BaseUUIDModel, UserBase, table=True):
    roles: list["UserRoles"] | None = Relationship(
        # sa_relationship_kwargs={"lazy": "joined"}
    )
    user_login: UserLogin | None = Relationship()


class UserRoles(BaseIDModel, table=True):
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="unique_user_role"),)

    user_id: uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE")
    role_id: uuid.UUID = Field(foreign_key="role.id", ondelete="CASCADE")

    role: "Role" = Relationship()
