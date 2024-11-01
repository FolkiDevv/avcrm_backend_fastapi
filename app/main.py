import time
from contextlib import AbstractAsyncContextManager, asynccontextmanager

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.context import correlation_id
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.api.v1.api import api_router as api_router_v1
from app.core.config import ModeEnum, settings
from app.core.tasks import unlink_unused_files
from app.utils.custom_logging import setup_logging
from app.utils.rate_limit import limiter

setup_logging(json_logs=settings.LOG_JSON_FORMAT, log_level=settings.LOG_LEVEL)
access_logger = structlog.stdlib.get_logger("api.access")
logger = structlog.stdlib.get_logger()


async def schedule_tasks() -> None:
    scheduler.add_job(
        unlink_unused_files,
        "interval",
        minutes=settings.STORAGE_CLEANUP_INTERVAL,
        id="unlink_unused_files",
    )


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AbstractAsyncContextManager[None]:
    await schedule_tasks()
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    openapi_url=f"{settings.API_PATH}/openapi.json",
    lifespan=lifespan,
    debug=ModeEnum.development == settings.MODE,
    redoc_url=None,
    docs_url="/docs" if ModeEnum.development == settings.MODE else None,
)
scheduler = AsyncIOScheduler()

app.state.limiter = limiter  # type: ignore
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore


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
            # response.headers["X-Process-Time"] = str(process_time / 10**9)
        return response  # noqa: B012


# This middleware must be placed after the logging, to populate the context with
# the request ID
# NOTE: Why last??
# Answer: middlewares are applied in the reverse order of when they are added
# (you can verify this by debugging `app.middleware_stack` and recursively
# drilling down the `app` property).
app.add_middleware(CorrelationIdMiddleware)  # type: ignore

app.add_middleware(SlowAPIMiddleware)  # type: ignore

# Add Routers
app.include_router(api_router_v1, prefix=settings.API_PATH)
