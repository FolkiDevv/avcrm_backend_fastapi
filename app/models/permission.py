from sqlmodel import Field

from app.models.base import BaseIDModel


class Permission(BaseIDModel, table=True):
    name: str = Field(nullable=False, unique=True)
    description: str | None = Field(default=None, nullable=True)