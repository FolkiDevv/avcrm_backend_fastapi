import uuid

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from app.models.base import BaseIDModel, BaseUUIDModel


class Role(BaseUUIDModel, table=True):
    name: str
    description: str | None = Field(default=None, nullable=True)

    permissions: list["RolePermission"] | None = Relationship(cascade_delete=True)


class RolePermission(BaseIDModel, table=True):
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="unique_role_permission"),
    )

    role_id: uuid.UUID = Field(foreign_key="role.id", ondelete="CASCADE")
    permission_id: int = Field(foreign_key="permission.id", ondelete="CASCADE")
