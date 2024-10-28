from hashlib import md5
from typing import TYPE_CHECKING, Annotated
from urllib.parse import quote
from uuid import UUID

import aiofiles
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Security,
    UploadFile,
)
from fastapi.responses import FileResponse
from sqlalchemy import exc
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import get_auth_user
from app.crud.attach import CRUDAttach
from app.db import get_session
from app.models import Attach
from app.schemas.attach import AttachRead, AttachUpdate
from app.utils.filepath import get_filepath

if TYPE_CHECKING:
    from app.models import User

router = APIRouter()


@router.get("/{attach_id}/d")
async def download_attach(
    attach_id: UUID,
    _: Annotated["User", Security(get_auth_user, scopes=("attach.get",))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    attach = await CRUDAttach(session).fetch(attach_id)
    if attach is None:
        raise HTTPException(status_code=404, detail="Attach not found")

    safe_filename = quote(attach.original_name)

    return FileResponse(
        attach.path,
        media_type=attach.content_type,
        headers={"Content-Disposition": f"inline; filename*=utf-8''{safe_filename}"},
    )


@router.get("/{attach_id}", response_model=AttachRead)
async def get_attach_data(
    attach_id: UUID,
    _: Annotated["User", Security(get_auth_user, scopes=("attach.get",))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    attach = await CRUDAttach(session).fetch(attach_id, selectinload_fields=["*"])
    if attach is None:
        raise HTTPException(status_code=404, detail="Attach not found")

    return attach


@router.get("", response_model=list[AttachRead])
async def get_attachs(
    request_id: Annotated[UUID, Query()],
    _: Annotated["User", Security(get_auth_user, scopes=("request.get", "attach.get"))],
    session: Annotated[AsyncSession, Depends(get_session)],
    skip: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query()] = 100,
    ids: Annotated[list[UUID] | None, Query()] = None,
    group_id: Annotated[int | None, Query()] = None,
):
    statement = select(Attach).where(col(Attach.request_id) == request_id)

    if ids is not None:
        statement = statement.where(col(Attach.id).in_(ids))
    if group_id is not None:
        statement = statement.where(col(Attach.group_id) == group_id)

    return await CRUDAttach(session).fetch_many(skip, limit, statement)


@router.put("/{attach_id}", response_model=AttachRead)
async def update_attach(
    attach_id: UUID,
    updated_attach: AttachUpdate,
    _: Annotated["User", Security(get_auth_user, scopes=("attach.update",))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    attach = await CRUDAttach(session).fetch(attach_id)
    if attach is None:
        raise HTTPException(status_code=404, detail="Attach not found")

    try:
        attach = await CRUDAttach(session).update(attach, updated_attach)
    except exc.IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Attach Group not exists",
        ) from e
    await attach.awaitable_attrs.group
    return attach


@router.delete("/{attach_id}", response_model=AttachRead)
async def remove_attach(
    attach_id: UUID,
    _: Annotated["User", Security(get_auth_user, scopes=("attach.remove",))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    attach = await CRUDAttach(session).fetch(attach_id, selectinload_fields=["*"])
    if attach is None:
        raise HTTPException(status_code=404, detail="Attach not found")

    attach_read = AttachRead.model_validate(attach)

    await CRUDAttach(session).remove(attach)

    return attach_read


@router.post("", response_model=AttachRead, status_code=201)
async def upload_attach(
    request_id: Annotated[UUID, Form()],
    file: Annotated[UploadFile, File()],
    user: Annotated["User", Security(get_auth_user, scopes=("attach.create",))],
    session: Annotated[AsyncSession, Depends(get_session)],
    group_id: Annotated[int | None, Form()] = None,
):
    # Generate file checksum to avoid collisions and duplicates
    filehash = md5()
    while contents := await file.read(128 * filehash.block_size):
        filehash.update(contents)
    path, filename = get_filepath(filehash.hexdigest())

    try:
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        path = path.joinpath(filename)
        # Skip if file already exists, checksum guarantee that exists file is the same
        if not path.exists():
            async with aiofiles.open(path, "wb") as out_file:
                await file.seek(0)
                while content := await file.read(1024):
                    await out_file.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="There was an error uploading the file"
        ) from e
    else:
        try:
            attach = Attach(
                request_id=request_id,
                path=str(path),
                size=file.size,
                content_type=file.content_type,
                original_name=file.filename,
                group_id=group_id,
                creator_id=user.id,
            )
            session.add(attach)
            await session.commit()

            await session.refresh(attach)
            await attach.awaitable_attrs.group

            return attach
        except exc.IntegrityError as e:
            await session.rollback()
            raise HTTPException(
                status_code=409,
                detail="Foreign key constraint failed",
            ) from e
    finally:
        await file.close()
