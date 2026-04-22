from pprint import pprint
from typing import Optional

import typer

from ynab_import import __version__
from ynab_import.core import import_transactions
from ynab_import.settings import Settings
from ynab_import.setup import create_reader, create_writer

app = typer.Typer(name="Ynab Import CLI")
state: dict = {"verbose": False}


def version_callback(value: bool):
    if value:
        typer.echo(f"CLI Version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    verbose: bool = False,
    version: Optional[bool] = typer.Option(None, "--version", callback=version_callback),
):
    """
    CLI for managing read/transform/import operations
    """
    if verbose:
        state["verbose"] = True
    state["config"] = Settings()


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
    Read transactions from a specified source and print in STD out
    """
    settings = state["config"]
    typer.echo(f"Reading transactions with config {settings.dict()}")
    typer.echo("Transactions loaded from reader")

    reader = create_reader(settings)
    typer.echo(reader.read_transactions())


@app.command()
def read_write() -> None:
    """
    Read transactions from a specified source and write to a specified destination
    """
    settings = state["config"]
    typer.echo("Importing transactions")

    reader = create_reader(settings)
    writer = create_writer(settings)

    import_transactions(reader, writer)


@app.command(name="import")
def run_import() -> None:
    """
    Read/Import transactions from source to destination
    """
    settings = state["config"]
    typer.echo(f"Import transactions with config {settings.dict()}")

    reader = create_reader(settings)
    writer = create_writer(settings)

    import_transactions(reader, writer)
