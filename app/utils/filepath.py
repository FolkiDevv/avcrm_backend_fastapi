import uuid
from pathlib import Path

from app.core.config import settings


def get_filepath(filename: str) -> tuple[Path, str]:
    filename = uuid.uuid3(uuid.NAMESPACE_DNS, filename).hex
    return Path(
        f"{settings.STORAGE_PATH}/{filename[:2]}/{filename[2:4]}"
    ), f"{filename}"
