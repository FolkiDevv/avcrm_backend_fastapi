from typing import ClassVar
from uuid import UUID

from app.models.attach import AttachBase
from app.schemas.attach_group import AttachGroupRead
from app.utils.partial import optional


class AttachCUBase(AttachBase):
    path: ClassVar
    size: ClassVar
    content_type: ClassVar
    creator_id: ClassVar


class AttachCreate(AttachCUBase):
    original_name: ClassVar


@optional()
class AttachUpdate(AttachCUBase):
    request_id: ClassVar


class AttachRead(AttachBase):
    id: UUID
    group: AttachGroupRead | None
    group_id: ClassVar
    path: ClassVar
