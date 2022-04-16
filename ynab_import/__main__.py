"""Invoke as `ynab-import' or `python -m ynab_import'.
"""
from pathlib import Path
from pprint import pprint

import typer
from pydantic import ValidationError

from ynab_import.common import ReaderKind, Settings, WriterKind

app = typer.Typer()
state = {"verbose": False}


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


@app.command(name="import")
def cli() -> None:
    """
    Read/Import transactoins from source to destination
    """
    settings = state["config"]
    typer.echo(f"Import transactions with conifg {settings.dict()}")
