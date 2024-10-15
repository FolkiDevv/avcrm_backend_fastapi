from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends, Query, Security
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import get_auth_user
from app.crud.user import CRUDUser
from app.db import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.utils.bcrypt import get_password_hash

router = APIRouter()


@router.get("/me", response_model=UserRead)
async def user_me(current_user: Annotated[User, Security(get_auth_user)]):
    return current_user


@router.get("/{user_id}", response_model=UserRead)
async def get_user_by_id(
    user_id: UUID,
    _: Annotated[User, Security(get_auth_user, scopes=("user.get",))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await CRUDUser(session).fetch(id=user_id)


@router.get("/", response_model=list[UserRead])
async def get_users(
    _: Annotated[User, Security(get_auth_user, scopes=("user.get",))],
    session: Annotated[AsyncSession, Depends(get_session)],
    skip: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query()] = 100,
    ids: Annotated[list[UUID] | None, Query()] = None,
    first_name: Annotated[str | None, Query()] = None,
    last_name: Annotated[str | None, Query()] = None,
):
    statement = select(User)

    if ids is not None:
        statement = statement.where(col(User.id).in_(ids))
    if first_name is not None:
        statement = statement.where(col(User.first_name).contains(first_name))
    if last_name is not None:
        statement = statement.where(col(User.last_name).contains(last_name))

    return await CRUDUser(session).fetch_many(skip, limit, statement)


@router.post("/{user_id}", response_model=UserRead)
async def update_user_by_id(
    user_id: UUID,
    updated_user: UserUpdate,
    _: Annotated[User, Security(get_auth_user, scopes=("user.update",))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    crud_user = CRUDUser(session)
    user = await crud_user.fetch(id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if updated_user.password:
        updated_user.password = get_password_hash(updated_user.password)

    return await crud_user.update(user, updated_user)


@router.delete("/{user_id}", response_model=UserRead)
async def remove_user_by_id(
    user_id: UUID,
    current_user: Annotated[User, Security(get_auth_user, scopes=("user.remove",))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="You can't delete yourself")

    return await CRUDUser(session).remove(user_id)


@router.put("/", response_model=UserRead)
async def create_user(
    new_user: UserCreate,
    _: Annotated[User, Security(get_auth_user, scopes=("user.create",))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    crud_user = CRUDUser(session)

    new_user.password = get_password_hash(new_user.password)

    return await crud_user.create(new_user)
