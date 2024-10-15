import enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Column, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseUUIDModel

if TYPE_CHECKING:
    from app.models import Client


class RequestStatus(enum.IntEnum):
    NEW = 0  # Новая
    RAW_SCHEME = 1  # Первичный чертеж
    ON_MEASURE = 2  # Замер
    FINALLY_SCHEME = 3  # Окончательный чертеж
    COORDINATION = 4  # Согласование
    ORDER = 5  # Заказ сформирован
    LOST = 7  # Сорвалась
    COMPLETED = 9  # Завершена
    FAKE = 8  # Не настоящая  # noqa: RUF003


class RequestBase(SQLModel):
    status: RequestStatus = Field(
        default=RequestStatus.NEW, sa_column=Column(Enum(RequestStatus))
    )
    note: str | None = Field(default=None, nullable=True)
    number_in_program: str | None = Field(default=None, nullable=True)
    changes_history: dict[str, str] | None = Field(
        default=None, nullable=True, sa_type=JSONB
    )  # JSON {"01.01.2000": "some text", "02.02.2000": "some other text"}

    client_id: UUID = Field(foreign_key="client.id", ondelete="CASCADE")
    request_service_id: int = Field(foreign_key="request_service.id")


class Request(BaseUUIDModel, RequestBase, table=True):
    client: "Client" = Relationship(back_populates="requests")
