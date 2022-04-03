"""Invoke as `ynab-import' or `python -m ynab_import'.
"""
import typer

from ynab_import.setup import create_reader, create_writer
from ynab_import.common.settings import ReaderKind, WriterKind
from ynab_import.core import import_transactions

app = typer.Typer(add_completion=False)


@app.command()
def cli(
    reader: ReaderKind = ReaderKind.swedbank_csv,
    writer: WriterKind = WriterKind.ynab_api,
):
    reader = create_reader(reader)
    writer = create_writer(writer)
    count = import_transactions(read=reader, write=writer)
    message = f"Transaction(s) imported: N {count} " + typer.style(
        "good", fg=typer.colors.GREEN, bold=True
    )
    typer.echo(message)


app()
