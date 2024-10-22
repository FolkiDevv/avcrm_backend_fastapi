from enum import Enum
from uuid import UUID

from pydantic_settings import BaseSettings


class ModeEnum(str, Enum):
    development = "dev"
    production = "prod"
    testing = "test"


class LogLevelEnum(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Settings(BaseSettings):
    MODE: ModeEnum = ModeEnum.development
    LOG_LEVEL: LogLevelEnum = LogLevelEnum.DEBUG
    LOG_JSON_FORMAT: bool = False
    PROJECT_NAME: str = "AVCRM"
    API_VERSION: str = "v1"
    API_V1_STR: str = f"/api/{API_VERSION}"
    STORAGE_PATH: str = "uploads"
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    STORAGE_CLEANUP_INTERVAL: int = 10  # minutes
    DEFAULT_RATE_LIMIT: int = 10
    MAX_LOGIN_ATTEMPTS: int = 3
    MAX_LOGIN_ATTEMPTS_BLOCK_TIME: int = 5
    MAX_LOGIN_ATTEMPTS_PERIOD: int = 15  # minutes

    SUPERUSER_ID: UUID | None = None


settings = Settings()  # pyright: ignore [reportCallIssue]
