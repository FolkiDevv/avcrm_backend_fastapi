import asyncio
from functools import wraps

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


@app.command(
    short_help="Create a new user in the database",
)
@coro
async def create_user(username: str, password: str):
    typer.echo(f"Creating user {username} with password {password}")
    password = get_password_hash(password)
    async with AsyncSession(engine) as session:
        user = User(
            username=username,
            password=password,
            first_name=username.title(),
            last_name=username.title(),
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
