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
    changes_history: dict[datetime, str] | None


class RequestCreate(RequestBaseCU):
    client_id: ClassVar
    status: ClassVar


@optional()
class RequestUpdate(RequestBaseCU):
    pass


class RequestRead(RequestBase):
    id: UUID
    client: ClientRead
    client_id: ClassVar
