from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, requests
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.security import (
    authenticate_user,
    create_access_token,
)
from app.db import get_session
from app.models import UserLoginSucceed
from app.schemas.security import TokenScheme
from app.utils.rate_limit import limiter

router = APIRouter()


@router.post("")
@limiter.limit("3/minute")
async def login_for_access_token(
    request: requests.Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TokenScheme:
    user = await authenticate_user(form_data.username, form_data.password, session)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
        },
        expires_delta=access_token_expires,
    )

    user_login_succeed = UserLoginSucceed(
        user_id=user.id,
        agent_data={
            "user_agent": request.headers.get("User-Agent"),
        },
    )
    session.add(user_login_succeed)
    await session.commit()

    return TokenScheme(access_token=access_token, token_type="bearer")
