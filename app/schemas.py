from pydantic import EmailStr
from sqlmodel import Field, SQLModel, Relationship
import uuid

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    first_name: str
    last_name: str
    email: EmailStr = Field(
        sa_type=str,
        nullable=False,
    )

    is_staff: bool
    is_client: bool
    is_active: bool

    roles: list["UserRoles"] = Relationship()


class Permission(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, unique=True)
    description: str | None = Field(default=None, nullable=True)


class Role(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str | None = Field(default=None, nullable=True)

    permissions: list["RolePermission"] = Relationship()


class RolePermission(SQLModel, table=True):
    role_id: int = Field(foreign_key="role.id")
    permission_id: int = Field(foreign_key="permission.id")


class UserRoles(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id")
    role_id: int = Field(foreign_key="role.id")

    role: Role = Relationship()

