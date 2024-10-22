from uuid import UUID

from pydantic import BaseModel


class TokenScheme(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: UUID
    login_id: UUID
