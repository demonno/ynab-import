from enum import Enum

from pydantic import BaseSettings


class ReaderKind(str, Enum):
    swedbank_csv = "swedbank_csv"


class WriterKind(str, Enum):
    ynab_api = "ynab_api"
    memory = "memory"
    stdout = "stdout"


class Settings(BaseSettings):
    reader: ReaderKind
    writer: WriterKind
    read_from_path: str = ""

    ynab_api_key: str
    ynab_budget_id: str
    ynab_account_id: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
