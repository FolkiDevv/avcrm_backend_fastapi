from sqlmodel import Field, SQLModel

from app.models.base import BaseIDModel


class AttachGroupBase(SQLModel):
    title: str = Field(nullable=False)


class AttachGroup(BaseIDModel, AttachGroupBase, table=True):
    __tablename__ = "attach_group"

    pass
