from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.models.attach_group import AttachGroup
from app.models.base import BaseUUIDModel


class AttachBase(SQLModel):
    path: str
    original_name: str = Field(nullable=True, default=None)
    content_type: str = Field(nullable=True, default=None)
    size: int

    creator_id: UUID = Field(foreign_key="user.id")
    group_id: int | None = Field(
        foreign_key="attach_group.id", nullable=True, default=None
    )

    request_id: UUID = Field(foreign_key="request.id", default=None, nullable=True)


class Attach(BaseUUIDModel, AttachBase, table=True):
    group: AttachGroup | None = Relationship()
