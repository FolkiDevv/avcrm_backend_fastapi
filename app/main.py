import time
from typing import Annotated

import structlog
from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.context import correlation_id
from fastapi import FastAPI
from fastapi.params import Security
from starlette.requests import Request
from starlette.responses import Response

from app.api.v1.api import api_router as api_router_v1
from app.core.config import settings
from app.core.security import (
    User,
    get_current_active_user,
)
from app.models.user import UserPublic
from app.utils.custom_logging import setup_logging

setup_logging(json_logs=settings.LOG_JSON_FORMAT, log_level=settings.LOG_LEVEL)

access_logger = structlog.get_logger("api.access")

logger = structlog.get_logger()

# @asynccontextmanager
# async def lifespan(fastapi_app: FastAPI):
#     await logger.info("App is starting")
#     yield
#     await logger.info("App is shutting down")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    # lifespan=lifespan,
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next) -> Response:
    structlog.contextvars.clear_contextvars()
    # These context vars will be added to all log entries emitted during the request
    request_id = correlation_id.get()
    structlog.contextvars.bind_contextvars(request_id=request_id)

    start_time = time.perf_counter_ns()
    # If the call_next raises an error, we still want to return our own 500 response,
    # so we can add headers to it (process time, request ID...)
    response = Response(status_code=500)
    try:
        response = await call_next(request)
    except Exception:
        # TODO: Validate that we don't swallow exceptions (unit test?)
        structlog.stdlib.get_logger("api.error").exception("Uncaught exception")
        raise
    finally:
        process_time = time.perf_counter_ns() - start_time
        status_code = response.status_code
        url = str(request.url)
        if request.client:
            client_host = request.client.host
            client_port = request.client.port
            http_method = request.method
            http_version = request.scope["http_version"]
            # Recreate the Uvicorn access log format, but add all parameters
            # as structured information
            access_logger.info(
                f"{client_host}:{client_port} - "
                f'"{http_method} {url} HTTP/{http_version}" {status_code}',
                http={
                    "url": str(request.url),
                    "status_code": status_code,
                    "method": http_method,
                    "request_id": request_id,
                    "version": http_version,
                },
                network={"client": {"ip": client_host, "port": client_port}},
                duration=process_time,
            )
            response.headers["X-Process-Time"] = str(process_time / 10**9)
        return response  # noqa: B012


# This middleware must be placed after the logging, to populate the context with
# the request ID
# NOTE: Why last??
# Answer: middlewares are applied in the reverse order of when they are added
# (you can verify this by debugging `app.middleware_stack` and recursively
# drilling down the `app` property).
app.add_middleware(CorrelationIdMiddleware)  # type: ignore


@app.get("/")
def hello():
    # custom_structlog_logger = structlog.get_logger("my.structlog.logger")
    # custom_structlog_logger.info("This is an info message from Structlog")
    # custom_structlog_logger.warning(
    #     "This is a warning message from Structlog, with attributes",
    #     an_extra="attribute")
    # custom_structlog_logger.error("This is an error message from Structlog")

    return "Hello, World!"


@app.get("/users/me/", response_model=UserPublic)
async def read_users_me(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["me"])],
):
    return current_user


# @app.get("/users/new/")
# async def read_own_items(
#     session: Annotated[AsyncSession, Depends(get_session)],
# ):
#     user = User(
#         username="test",
#         password=get_password_hash("test"),
#         first_name="Mr",
#         last_name="Test",
#     )
#     session.add(user)
#     await session.commit()
#     return user


# Add Routers
app.include_router(api_router_v1, prefix=settings.API_V1_STR)
