from fastapi import APIRouter

from app.api.v1.endpoints import attach, client, login, request, user

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(client.router, prefix="/clients", tags=["clients"])
api_router.include_router(request.router, prefix="/requests", tags=["requests"])
api_router.include_router(attach.router, prefix="/attachs", tags=["attachs"])
