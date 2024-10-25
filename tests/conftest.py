import os
from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.db import get_session
from app.main import app
from app.models import *  # noqa: F403
from app.utils.bcrypt import get_password_hash

url = "http://test"
engine = create_async_engine(os.getenv("TEST_DATABASE_URL"), echo=True, future=True)


async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session


app.state.limiter.enabled = False
app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
async def setup_db(anyio_backend):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture(scope="session")
async def ac(anyio_backend):
    async with AsyncClient(transport=ASGITransport(app=app), base_url=url) as client:
        yield client


@pytest.fixture()
async def session(anyio_backend):
    async with AsyncSession(engine) as session:
        yield session


@pytest.fixture()
async def create_user(anyio_backend, ac, session):
    async def _create_user(
        username: str, password: str, perms: list[str] | None = None
    ):
        user = User(
            username=username,
            first_name="Ivan",
            last_name="Tea",
            password=get_password_hash(password),
        )
        session.add(user)

        user_role = Role(name=username)
        session.add(user_role)

        # Фиксируем изменения для получения ID роли и пользователя
        await session.flush()

        # Обрабатываем список разрешений
        if perms:
            for perm_name in perms:
                # Проверяем, существует ли уже разрешение
                stmt = select(Permission).where(Permission.name == perm_name)
                result = await session.exec(stmt)
                permission = result.one_or_none()

                # Создаем разрешение, если оно отсутствует
                if not permission:
                    permission = Permission(
                        name=perm_name, description=f"{perm_name} permission"
                    )
                    session.add(permission)
                    await session.flush()  # Чтобы получить ID разрешения

                # Создаем связь между ролью и разрешением
                role_permission = RolePermission(
                    role_id=user_role.id, permission_id=permission.id
                )
                session.add(role_permission)

        # Добавляем роль пользователю
        user_role_link = UserRoles(user_id=user.id, role_id=user_role.id)
        session.add(user_role_link)

        await session.commit()
        await session.refresh(user)

        return user

    return _create_user


@pytest.fixture
def generate_token():
    def _generate_token(user_id: int, expired: bool = False):
        exp = datetime.now(UTC)
        exp += timedelta(minutes=5) if not expired else -timedelta(minutes=5)
        payload = {
            "sub": str(user_id),
            "login_id": str(user_id),
            "exp": exp,
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return _generate_token
