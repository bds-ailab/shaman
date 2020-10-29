"""Command Line application."""
import typer
import uvicorn


cli = typer.Typer()


@cli.command()
def dev(host: str = "0.0.0.0", port: int = 5000):
    """Run the application in development mode."""
    uvicorn.run("shaman_api:app",
                host=host,
                port=port,
                reload=True,
                access_log=False)


@cli.command()
def prod(
    host: str = "0.0.0.0",
    port: int = 8080,
    access_log: bool = False,
    workers: int = 2,
    loop: str = "uvloop",
):
    """Run the application in production mode."""
    uvicorn.run(
        "shaman_api:app",
        host=host,
        port=port,
        workers=workers,
        access_log=access_log,
        loop=loop,
        reload=False,
    )
