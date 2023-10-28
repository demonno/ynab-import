from pathlib import Path
from pprint import pprint
from typing import Optional

import typer
from pydantic import ValidationError

from ynab_import import __version__
from ynab_import.core import import_transactions
from ynab_import.settings import Settings
from ynab_import.setup import create_writer, create_reader

app = typer.Typer(name="Ynab Import CLI")
state = {"verbose": False}


def version_callback(value: bool):
    if value:
        typer.echo(f"CLI Version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    config: Path = typer.Option(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
    ),
    verbose: bool = False,
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback
    ),
):
    """
    CLI for managing read/transform/import operatoins
    """
    if verbose:
        state["verbose"] = True
    try:
        state["config"] = Settings(config)
    except ValidationError as exc:
        typer.echo("Invalid configuration")
        typer.echo(exc)


@app.command()
def check():
    """
    Print config to be used for importing
    """
    settings = state["config"]
    pprint(settings.dict())


@app.command()
def read() -> None:
    """
    Print transactions from specified source
    """
    settings = state["config"]
    typer.echo(f"Reading transactions with conifg {settings.dict()}")
    typer.echo(f"Transactions loaded from reader")

    reader = create_reader(settings)
    typer.echo(reader.read_transactions())

@app.command()
def import_transactions() -> None:
    """
    Print transactions from specified source
    """
    settings = state["config"]
    typer.echo("Importing transactions")

    reader = create_reader(settings)
    writer = create_writer(settings)

    import_transactions(reader, writer)

@app.command(name="import")
def cli() -> None:
    """
    Read/Import transactoins from source to destination
    """
    settings = state["config"]
    typer.echo(f"Import transactions with conifg {settings.dict()}")


