from pathlib import Path

import structlog
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.db import engine
from app.models import Attach


async def unlink_unused_files() -> None:
    storage_path = Path(settings.STORAGE_PATH)
    files_paths = set()
    for attach in storage_path.glob("**/*"):
        if attach.is_file():
            files_paths.add(str(attach))

    if not files_paths:
        return

    async with AsyncSession(engine) as session:
        used_files = set(
            await session.exec(
                select(Attach.path).filter(col(Attach.path).in_(files_paths))
            )
        )

    unused_files = files_paths - used_files

    logger = structlog.stdlib.get_logger("tasks.unlink_unused_files")
    logger.info(
        " ".join(
            (
                f"Files founded: {len(files_paths)};",
                f"used: {len(used_files)};",
                f"unused: {len(unused_files)}",
            )
        )
    )

    for file in unused_files:
        filepath = Path(file)
        if not filepath.exists():
            continue
        logger.info(f"Unlinking file: {file}")
        filepath.unlink()

        while (
            (parent := filepath.parent)
            and parent.is_dir()
            and parent.is_relative_to(storage_path)
        ):
            try:
                parent.rmdir()
            except OSError:
                # If the directory is not empty, we can't remove it
                break
