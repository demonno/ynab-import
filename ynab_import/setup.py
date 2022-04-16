from ynab_import.infra import SwedbankCSVReader
from ynab_import.settings import ReaderKind, Settings, WriterKind
from ynab_import.core.interactions import IReadRepository, IWriteRepository
from ynab_import.infra.http import RequestsClient
from ynab_import.infra.ynab import YnabAPIBasedRepository


def create_reader(settings: Settings, reader: ReaderKind) -> IReadRepository:
    if reader == ReaderKind.swedbank_csv:
        return SwedbankCSVReader(source_file_path=settings.read_from_path)

    raise NotImplementedError(f"{reader} reader is not implemented.")


def create_writer(settings: Settings, writer: WriterKind) -> IWriteRepository:
    if writer == WriterKind.ynab_api:
        return _create_ynab_api_reader()
    raise NotImplementedError(f"{writer} writer is not implemented.")


def _create_ynab_api_reader(settings: Settings):
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
