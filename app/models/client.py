from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseUUIDModel

if TYPE_CHECKING:
    from app.models import Request, User


class ClientBase(SQLModel):
    user_id: UUID = Field(foreign_key="user.id", ondelete="CASCADE")
    note: str | None = Field(nullable=True, default=None)


class Client(BaseUUIDModel, ClientBase, table=True):
    user: "User" = Relationship()
    requests: "Request" = Relationship(back_populates="client")
