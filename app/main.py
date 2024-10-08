from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    logger.info("App is starting")
    yield
    logger.info("App is shutting down")

app = FastAPI(lifespan=lifespan)

@app.get("/")
def hello():
    return {"Hello": "World"}
