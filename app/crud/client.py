from fastapi import HTTPException
from sqlalchemy import exc
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import CRUDBase
from app.models import Client, User
from app.schemas.client import ClientCreate, ClientUpdate
from app.utils.translit import transliterate


class CRUDClient(CRUDBase[Client, ClientCreate, ClientUpdate]):
    model = Client

    async def create(
        self, obj_in: ClientCreate, db_session: AsyncSession | None = None
    ) -> Client:
        db_session = db_session or self.session

        try:
            # user = User(
            #     username=transliterate(obj_in.first_name + obj_in.last_name).lower(),
            #     first_name=obj_in.first_name,
            #     last_name=obj_in.last_name,
            #     email=obj_in.email,
            #     phone=obj_in.phone,
            # )
            user = User.model_validate(
                obj_in,
                update={
                    "username": transliterate(
                        obj_in.first_name + obj_in.last_name
                    ).lower(),
                    "password": None,
                },
            )
            db_session.add(user)
            await db_session.commit()
            await db_session.refresh(user)

            db_obj = self.model.model_validate(obj_in, update={"user_id": user.id})
            db_obj.user = user

            db_session.add(db_obj)
            await db_session.commit()
        except exc.IntegrityError as err:
            await db_session.rollback()
            raise HTTPException(
                status_code=409,
                detail="Client already exists",
            ) from err
        await db_session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        obj_current: Client,
        obj_new: ClientUpdate,
        db_session: AsyncSession | None = None,
    ) -> Client:
        db_session = db_session or self.session

        update_data = obj_new.model_dump(exclude_unset=True)
        for field in update_data:
            if field in obj_current.model_fields:
                setattr(obj_current, field, update_data[field])
            else:
                setattr(obj_current.user, field, update_data[field])

        db_session.add(obj_current.user)
        db_session.add(obj_current)
        await db_session.commit()
        await db_session.refresh(obj_current)
        return obj_current
