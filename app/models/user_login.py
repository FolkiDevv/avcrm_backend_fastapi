from datetime import datetime
from uuid import UUID

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from app.models.base import BaseUUIDModel


class UserLoginBase(SQLModel):
    user_id: UUID = Field(
        foreign_key="user.id", ondelete="CASCADE", nullable=False, primary_key=True
    )

    attempts: int = Field(nullable=False, default=1)
    last_attempt_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )

    blocked_before: datetime | None = Field(default=None, nullable=True)


class UserLogin(UserLoginBase, table=True):
    __tablename__ = "user_login"


class UserLoginSucceedBase(SQLModel):
    user_id: UUID = Field(foreign_key="user.id", ondelete="CASCADE", nullable=False)
    agent_data: dict = Field(sa_type=JSONB)


class UserLoginSucceed(BaseUUIDModel, UserLoginSucceedBase, table=True):
    __tablename__ = "user_login_succeed"
