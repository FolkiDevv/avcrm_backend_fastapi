from fastapi import APIRouter

from app.api.v1.endpoints import attach, attach_group, client, login, request, user

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(client.router, prefix="/clients", tags=["clients"])
api_router.include_router(request.router, prefix="/requests", tags=["requests"])
api_router.include_router(attach.router, prefix="/attachs", tags=["attachs"])
api_router.include_router(
    attach_group.router, prefix="/attachs/groups", tags=["attachs"]
)
