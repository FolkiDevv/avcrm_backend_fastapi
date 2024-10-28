from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Security
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import get_auth_user
from app.crud.attach_group import CRUDAttachGroup
from app.db import get_session
from app.models import AttachGroup, User
from app.schemas.attach_group import (
    AttachGroupCreate,
    AttachGroupRead,
    AttachGroupUpdate,
)

router = APIRouter()


@router.get("/{attach_group_id}", response_model=AttachGroupRead)
async def get_attach_group(
    attach_group_id: int,
    _: Annotated["User", Security(get_auth_user, scopes=("attach.get",))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    attach_group = await CRUDAttachGroup(session).fetch(attach_group_id)
    if attach_group is None:
        raise HTTPException(status_code=404, detail="Attach Group not found")
    return attach_group


@router.get("", response_model=list[AttachGroupRead])
async def get_attach_groups(
    _: Annotated["User", Security(get_auth_user, scopes=("attach.get",))],
    session: Annotated[AsyncSession, Depends(get_session)],
    skip: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query()] = 100,
    ids: Annotated[list[int] | None, Query()] = None,
):
    statement = select(AttachGroup)

    if ids is not None:
        statement = statement.where(col(AttachGroup.id).in_(ids))

    return await CRUDAttachGroup(session).fetch_many(skip, limit, statement)


@router.put("/{attach_group_id}", response_model=AttachGroupRead)
async def update_attach_group(
    attach_group_id: int,
    updated_attach_group: AttachGroupUpdate,
    _: Annotated["User", Security(get_auth_user, scopes=("attach.update",))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    crud_attach_group = CRUDAttachGroup(session)
    attach_group = await crud_attach_group.fetch(attach_group_id)
    if attach_group is None:
        raise HTTPException(status_code=404, detail="Attach Group not found")

    return await crud_attach_group.update(attach_group, updated_attach_group)


@router.delete("/{attach_group_id}", response_model=AttachGroupRead)
async def remove_attach_group(
    attach_group_id: int,
    _: Annotated["User", Security(get_auth_user, scopes=("attach.remove",))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    crud_attach_group = CRUDAttachGroup(session)
    attach_group = await crud_attach_group.fetch(attach_group_id)
    if attach_group is None:
        raise HTTPException(status_code=404, detail="Attach Group not found")

    return await crud_attach_group.remove(attach_group)


@router.post("", response_model=AttachGroupRead, status_code=201)
async def create_attach_group(
    new_attach_group: AttachGroupCreate,
    _: Annotated["User", Security(get_auth_user, scopes=("attach.create",))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await CRUDAttachGroup(session).create(new_attach_group)
