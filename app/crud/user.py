from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import CRUDBase
from app.models import User


class CRUDUser(CRUDBase[User, User, User]):
    async def fetch_by_username(
        self, *, username: str, db_session: AsyncSession | None = None
    ) -> User | None:
        db_session = db_session or self.session
        query = select(User).where(User.username == username)
        response = await db_session.exec(query)
        return response.one_or_none()
