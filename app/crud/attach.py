from app.crud.base import CRUDBase
from app.models import Attach
from app.schemas.attach import AttachCreate, AttachUpdate


class CRUDAttach(CRUDBase[Attach, AttachCreate, AttachUpdate]):
    model = Attach
