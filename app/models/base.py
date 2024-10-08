import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class BaseCUTimeModel(SQLModel):
    updated_at: datetime | None = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now}
    )
    created_at: datetime | None = Field(default_factory=datetime.now)

class BaseUUIDModel(BaseCUTimeModel):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )

class BaseIDModel(BaseCUTimeModel):
    id: int | None = Field(
        default=None,
        primary_key=True,
        index=True,
        nullable=False,
    )