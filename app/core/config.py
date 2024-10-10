from enum import Enum

from pydantic_settings import BaseSettings


class ModeEnum(str, Enum):
    development = "development"
    production = "production"
    testing = "testing"


class LogLevelEnum(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    MODE: ModeEnum = ModeEnum.development
    LOG_LEVEL: LogLevelEnum = LogLevelEnum.DEBUG
    LOG_JSON_FORMAT: bool = False
    PROJECT_NAME: str = "AVCRM"
    API_VERSION: str = "v1"
    API_V1_STR: str = f"/api/{API_VERSION}"
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


settings = Settings()  # pyright: ignore [reportCallIssue]
