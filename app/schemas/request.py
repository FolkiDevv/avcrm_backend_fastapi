from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlmodel import Field

from app.models.request import RequestBase
from app.schemas.client import ClientRead
from app.utils.partial import optional


class RequestBaseCU(RequestBase):
    first_name: str = Field(min_length=2, max_length=50, nullable=False)
    phone: PhoneNumber | None = Field()
    changes_history: dict[datetime, str] | None = Field(default=None)


class RequestCreateWithNewClient(RequestBaseCU):
    client_id: ClassVar
    status: ClassVar
    changes_history: ClassVar


class RequestCreate(RequestBaseCU):
    status: ClassVar
    phone: ClassVar
    first_name: ClassVar
    changes_history: ClassVar


@optional()
class RequestUpdate(RequestBaseCU):
    phone: ClassVar
    first_name: ClassVar
    changes_history: ClassVar


class RequestRead(RequestBase):
    id: UUID
    client: ClientRead
    client_id: ClassVar
