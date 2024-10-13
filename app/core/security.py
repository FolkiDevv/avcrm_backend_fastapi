from datetime import UTC, datetime, timedelta
from typing import Annotated, Literal
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jwt.exceptions import InvalidTokenError
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession
from structlog.stdlib import get_logger

from app.core.config import settings
from app.crud.user import CRUDUser
from app.db import get_session
from app.models import Permission, RolePermission, User, UserRoles
from app.schemas.security import TokenData
from app.utils.bcrypt import verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")


async def authenticate_user(
    username: str, password: str, session: AsyncSession
) -> User | Literal[False]:
    user = await CRUDUser(session).fetch_by_username(username=username)
    if not user or not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def __get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User | None:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if (user_id := payload.get("sub")) is None:
            raise credentials_exception
        token_data = TokenData.model_validate({"id": UUID(user_id)})
    except InvalidTokenError as err:
        raise credentials_exception from err

    user = await CRUDUser(session).fetch(id=token_data.id)
    if not user:
        raise credentials_exception

    statement = (
        select(Permission)
        .where(User.id == token_data.id)
        .where(
            col(Permission.id).in_(
                select(RolePermission.permission_id).where(
                    col(RolePermission.role_id).in_(
                        select(UserRoles.role_id).where(
                            UserRoles.user_id == token_data.id
                        )
                    )
                )
            )
        )
    )

    logger = get_logger(__name__)

    res = (await session.exec(statement)).all()

    permissions = {perm.name for (_, perm) in res}

    logger.debug(str(permissions))
    if user.id != settings.SUPERUSER_ID:
        for scope in security_scopes.scopes:
            if scope not in permissions:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": "Bearer"},
                )
    return user


async def get_auth_user(
    current_user: Annotated[User, Depends(__get_current_user)],
) -> User | None:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
