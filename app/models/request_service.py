from sqlmodel import Field, SQLModel

from app.models.base import BaseIDModel


class RequestServiceBase(SQLModel):
    name: str = Field(
        nullable=False,
        unique=True,
        schema_extra={"pattern": r"^[a-z0-9_]+$"},
    )
    display_name: str = Field(nullable=False)


class RequestService(BaseIDModel, RequestServiceBase, table=True):
    __tablename__ = "request_service"
