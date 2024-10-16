from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Security
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import get_auth_user
from app.crud.request import CRUDRequest
from app.db import get_session
from app.models import Client, Request, User
from app.schemas.request import RequestCreate, RequestRead, RequestUpdate

router = APIRouter()


@router.get("/{request_id}", response_model=RequestRead)
async def get_request(
    request_id: UUID,
    _: Annotated["User", Security(get_auth_user, scopes=("request.get",))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    request = await CRUDRequest(session).fetch(id=request_id)
    await request.awaitable_attrs.client
    return request


@router.get("", response_model=list[RequestRead])
async def get_requests(
    _: Annotated["User", Security(get_auth_user, scopes=("request.get",))],
    session: Annotated[AsyncSession, Depends(get_session)],
    skip: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query()] = 100,
    ids: Annotated[list[UUID] | None, Query()] = None,
    first_name: Annotated[str | None, Query()] = None,
):
    statement = select(Request)

    if ids is not None:
        statement = statement.where(col(Request.id).in_(ids))
    if first_name:
        statement = (
            statement.join(Client)
            .join(User)
            .where(col(User.first_name).contains(first_name))
        )

    return await CRUDRequest(session).fetch_many(
        skip, limit, statement, selectinload_fields=["*"]
    )


@router.put("/{request_id}", response_model=RequestRead)
async def update_request(
    request_id: UUID,
    updated_request: RequestUpdate,
    _: Annotated["User", Security(get_auth_user, scopes=("request.update",))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    crud_request = CRUDRequest(session)
    request = await crud_request.fetch(request_id, selectinload_fields=["*"])
    if request is None:
        raise HTTPException(status_code=404, detail="Request not found")

    request = await crud_request.update(request, updated_request)
    await request.awaitable_attrs.client
    return request


@router.delete("/{request_id}", response_model=RequestRead)
async def remove_request(
    request_id: UUID,
    _: Annotated["User", Security(get_auth_user, scopes=("request.remove",))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    crud_request = CRUDRequest(session)
    request = await crud_request.fetch(request_id, selectinload_fields=["*"])
    if request is None:
        raise HTTPException(status_code=404, detail="Request not found")

    request_read = RequestRead.model_validate(request)

    await crud_request.remove(request)

    return request_read


@router.post("", status_code=201, response_model=RequestRead)
async def create_request(
    new_request: RequestCreate,
    _: Annotated["User", Security(get_auth_user, scopes=("request.create",))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    request = await CRUDRequest(session).create(new_request)
    await request.awaitable_attrs.client
    await request.client.awaitable_attrs.user
    return request
