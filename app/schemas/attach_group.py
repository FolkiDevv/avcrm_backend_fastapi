from app.models.attach_group import AttachGroupBase
from app.utils.partial import optional


class AttachGroupCreate(AttachGroupBase):
    pass


@optional()
class AttachGroupUpdate(AttachGroupBase):
    pass


class AttachGroupRead(AttachGroupBase):
    id: int
