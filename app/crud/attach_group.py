from app.crud.base import CRUDBase
from app.models import AttachGroup


class CRUDAttachGroup(CRUDBase[AttachGroup, AttachGroup, AttachGroup]):
    model = AttachGroup
