from app.crud.base import CRUDBase
from app.models import AttachGroup
from app.schemas.attach_group import AttachGroupCreate, AttachGroupUpdate


class CRUDAttachGroup(CRUDBase[AttachGroup, AttachGroupCreate, AttachGroupUpdate]):
    model = AttachGroup
