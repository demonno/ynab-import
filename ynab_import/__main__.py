"""Invoke as `ynab-import' or `python -m ynab_import'.
"""
from pydantic import ValidationError
import typer
from pprint import pprint

from pathlib import Path
import json
from ynab_import.common import ReaderKind, WriterKind, Settings
from ynab_import.core import import_transactions
from ynab_import.setup import create_reader, create_writer

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
        resolve_path=True
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
def read():
    """
    Print transactions from specified source
    """
    settings = state["config"]
    typer.echo(f"Reading transactions with conifg {settings.dict()}")


@app.command(name="import")
def cli(
    reader: ReaderKind,
    writer: WriterKind,
):
    """
    Read/Import transactoins from source to destination
    """
    settings = state["config"]
    typer.echo(f"Import transactions with conifg {settings.dict()}")