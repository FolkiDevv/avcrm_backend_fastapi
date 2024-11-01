import asyncio
from functools import wraps
from typing import Annotated

import typer
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import engine
from app.models import User
from app.utils.bcrypt import get_password_hash


def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


app = typer.Typer()


@app.command()
def hello(name: str):
    typer.echo(f"Hello {name}")


def username_validator(username: str) -> str:
    if len(username) < 5:
        raise typer.BadParameter("Username must be at least 5 characters long")
    return username


@app.command(
    short_help="Create a new user in the database",
)
@coro
async def create_user(
    username: Annotated[str, typer.Argument(callback=username_validator)],
):
    typer.echo(f"Creating user {username} with password same as username")
    password = get_password_hash(username)
    async with AsyncSession(engine) as session:
        user = User(
            username=username,
            password=password,
            first_name=username.title(),
            last_name=username.title(),
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        typer.echo(
            " ".join(
                (
                    typer.style("User created successfully!", fg=typer.colors.GREEN),
                    "ID:",
                    str(user.id),
                )
            )
        )


if __name__ == "__main__":
    app()
