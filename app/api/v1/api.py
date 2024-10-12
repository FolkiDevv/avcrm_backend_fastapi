from fastapi import APIRouter

from app.api.v1.endpoints import client, login, user

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(client.router, prefix="/client", tags=["client"])
