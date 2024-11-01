from datetime import UTC, datetime, timedelta
from math import ceil
from typing import Annotated
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
from app.models import Permission, RolePermission, User, UserLogin, UserRoles
from app.schemas.security import TokenData
from app.utils.bcrypt import verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PATH}/login")


async def authenticate_user(
    username: str, password: str, session: AsyncSession
) -> User:
    user = await CRUDUser(session).fetch_by_username(username=username)
    incorrect_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not user:
        raise incorrect_exc

    await user.awaitable_attrs.user_login

    dt_now = datetime.now()
    user_login = user.user_login

    def __format_security_exc() -> HTTPException:
        nonlocal dt_now, user_login
        wait_time = ceil((user_login.blocked_before - dt_now).total_seconds() / 60)
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account blocked. Too many login attempts. "
            f"Try again in {wait_time} minutes.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user_login is not None:
        user_login.attempts += 1
        if (
            user_login.blocked_before is not None
            and dt_now <= user_login.blocked_before
        ):
            # If the account is blocked, we raise an exception
            raise __format_security_exc()
        elif user_login.attempts >= settings.MAX_LOGIN_ATTEMPTS:
            if (
                dt_now - max(user_login.last_attempt_at, user_login.blocked_before)
            ).total_seconds() <= settings.MAX_LOGIN_ATTEMPTS_PERIOD * 60:
                # If the account has reached the maximum number of attempts, we block it
                user_login.blocked_before = dt_now + timedelta(
                    minutes=settings.MAX_LOGIN_ATTEMPTS_BLOCK_TIME * user_login.attempts
                )

                session.add(user_login)
                await session.commit()
                await user.awaitable_attrs.user_login

                raise __format_security_exc()
            else:
                # If the last unsuccessful login attempt was a long time ago,
                # reset the counter
                user.user_login.attempts = 1
    else:
        user_login = UserLogin(
            user_id=user.id,
        )
    session.add(user_login)
    await session.commit()
    await user.awaitable_attrs.user_login

    if not verify_password(password, user.password):
        raise incorrect_exc
    if user.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is not active. Contact the administrator.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # If auth is successful, we reset the number of attempts and blocked_before
    user_login.attempts = 0
    user_login.blocked_before = None
    session.add(user_login)
    await session.commit()
    await user.awaitable_attrs.user_login

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
        if (user_id := payload.get("sub")) is None or (
            login_id := payload.get("login_id")
        ) is None:
            raise credentials_exception
        token_data = TokenData.model_validate(
            {"id": UUID(user_id), "login_id": UUID(login_id)}
        )
    except InvalidTokenError as err:
        raise credentials_exception from err

    user = await CRUDUser(session).fetch(obj_id=token_data.id)
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

    permissions = {perm.name for perm in res}

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
