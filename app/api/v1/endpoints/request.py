from typing import TYPE_CHECKING, Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Security
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import get_auth_user
from app.crud.request import CRUDRequest
from app.db import get_session
from app.schemas.request import RequestCreate, RequestRead

if TYPE_CHECKING:
    from app.models import User

router = APIRouter()


@router.get("/{request_id}", response_model=RequestRead)
async def get_request_by_id(
    request_id: UUID,
    _: Annotated["User", Security(get_auth_user, scopes=("request.get",))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    request = await CRUDRequest(session).fetch(id=request_id)
    await request.awaitable_attrs.client
    return request


@router.put("/", response_model=RequestRead)
async def create_request(
    new_request: RequestCreate,
    _: Annotated["User", Security(get_auth_user, scopes=("request.create",))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    request = await CRUDRequest(session).create(new_request)
    await request.awaitable_attrs.client
    await request.client.awaitable_attrs.user
    return request
