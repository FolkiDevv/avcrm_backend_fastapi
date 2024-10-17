from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import exc
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import CRUDBase
from app.crud.client import CRUDClient
from app.models import Request
from app.schemas.client import ClientCreate
from app.schemas.request import RequestCreate, RequestUpdate


class CRUDRequest(CRUDBase[Request, RequestCreate, RequestUpdate]):
    model = Request

    async def create(
        self,
        obj_in: RequestCreate | Request,
        client_id: UUID | None = None,
        # created_by_id: UUID | str | None = None,
        db_session: AsyncSession | None = None,
    ) -> Request:
        db_session = db_session or self.session

        if client_id is None:
            client = await CRUDClient(db_session).create(
                ClientCreate.model_validate(obj_in), commit=False
            )
        else:
            client = await CRUDClient(db_session).fetch(client_id)
            if client is None:
                raise HTTPException(status_code=404, detail="Client not found")

        try:
            db_obj = self.model.model_validate(
                obj_in,
                update={
                    "client_id": client.id,
                    "changes_history": {
                        k.isoformat(): v for k, v in obj_in.changes_history.items()
                    }
                    if obj_in.changes_history
                    else None,
                },
            )

            db_session.add(db_obj)
            await db_session.commit()
        except exc.IntegrityError as err:
            await db_session.rollback()
            raise HTTPException(
                status_code=409,
                detail="Provided request service not exists",
            ) from err

        await db_session.refresh(db_obj)
        return db_obj
