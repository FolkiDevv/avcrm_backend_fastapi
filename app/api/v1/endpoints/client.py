from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Security
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import get_auth_user
from app.crud.client import CRUDClient
from app.crud.user import CRUDUser
from app.db import get_session
from app.models import Client
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate

router = APIRouter()


@router.get("/{client_id}", response_model=ClientRead)
async def get_client_by_id(
    client_id: UUID,
    _: Annotated[ClientRead, Security(get_auth_user, scopes=("client.get",))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    client = await CRUDClient(session).fetch(id=client_id)
    await client.awaitable_attrs.user
    return client


@router.get("/", response_model=list[ClientRead])
async def get_clients(
    _: Annotated[ClientRead, Security(get_auth_user, scopes=("client.get",))],
    session: Annotated[AsyncSession, Depends(get_session)],
    skip: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query()] = 100,
    ids: Annotated[list[UUID] | None, Query()] = None,
    first_name: Annotated[str | None, Query()] = None,
    last_name: Annotated[str | None, Query()] = None,
):
    statement = select(Client)

    if ids is not None:
        statement = statement.where(col(Client.id).in_(ids))
    if first_name is not None:
        statement = statement.where(col(Client.user.first_name).contains(first_name))
    if last_name is not None:
        statement = statement.where(col(Client.user.last_name).contains(last_name))

    return await CRUDClient(session).fetch_many(
        skip, limit, statement, joinedloads=[Client.user]
    )


@router.post("/{client_id}", response_model=ClientRead)
async def update_client_by_id(
    client_id: UUID,
    updated_client: ClientUpdate,
    _: Annotated[ClientRead, Security(get_auth_user, scopes=("client.update",))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    crud_client = CRUDClient(session)
    client = await crud_client.fetch(id=client_id, joinedloads=[Client.user])
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    client = await crud_client.update(client, updated_client)
    await client.awaitable_attrs.user
    return client


@router.delete("/{client_id}", response_model=ClientRead)
async def remove_client_by_id(
    client_id: UUID,
    _: Annotated[ClientRead, Security(get_auth_user, scopes=("client.remove",))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    client = await CRUDClient(session).fetch(client_id, joinedloads=[Client.user])
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    client_read = ClientRead.model_validate(client)

    await CRUDUser(session).remove(client.user_id)

    return client_read


@router.put("/", response_model=ClientRead)
async def create_client(
    new_user: ClientCreate,
    _: Annotated[ClientRead, Security(get_auth_user, scopes=("client.create",))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    client = await CRUDClient(session).create(new_user)
    await client.awaitable_attrs.user
    return client
