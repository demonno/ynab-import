import typer

from ynab_import.common.settings import ReaderKind, WriterKind, settings
from ynab_import.core import import_transactions
from ynab_import.core.interactions import IReadRepository, IWriteRepository
from ynab_import.infra.http import RequestsClient
from ynab_import.infra.ynab import YnabAPIBasedRepository
from ynab_import.swedbank.providers import SwedbankCSVReader


def create_reader(reader: ReaderKind) -> IReadRepository:
    if reader == ReaderKind.swedbank_csv:
        return SwedbankCSVReader(source_file_path=settings.read_from_path)

    raise NotImplementedError(f"{reader} reader is not implemented.")


def create_writer(writer: WriterKind) -> IWriteRepository:
    if writer == WriterKind.ynab_api:
        http_client = (
            RequestsClient()
            .with_base_url("https://api.youneedabudget.com/v1/")
            .with_timeout(5.0)
            .with_api_key_auth(settings.ynab_api_key)
        )
        return YnabAPIBasedRepository(
            http_client=http_client,
            budget_id=settings.ynab_budget_id,
            account_id=settings.ynab_account_id,
        )
    raise NotImplementedError(f"{writer} writer is not implemented.")


app = typer.Typer(add_completion=False)


@app.command()
def cli(
    reader: ReaderKind = ReaderKind.swedbank_csv,
    writer: WriterKind = WriterKind.ynab_api,
):
    reader = create_reader(reader)
    writer = create_writer(writer)
    count = import_transactions(read=reader, write=writer)
    message = f"Transaction(s) imported: N {count} " + typer.style("good", fg=typer.colors.GREEN, bold=True)
    typer.echo(message)


def main():
    app()
