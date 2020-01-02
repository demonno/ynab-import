import argparse
from typing import Dict, Any

from ynab_import.common import settings
from ynab_import.revolut.providers import RevolutCSVProvider
from ynab_import.revolut.transformers import RevolutTransformer
from ynab_import.swedbank.providers import SwedbankCSVProvider
from ynab_import.swedbank.transformers import SwedBankTransformer
from ynab_import.ynab.providers import YnabBudget


def parse_args() -> Dict[str, Any]:
    parser = argparse.ArgumentParser(
        description="Prepare and/or import transactions to ynab.com from different sources"
    )
    parser.add_argument(
        "-s",
        "--source",
        dest="source",
        # required=True,
        choices=["swedbank", "revolut"],
        help="Specify source of your transactions[swedbank,revolut]",
    )
    parser.add_argument(
        "-r",
        "--read-from",
        dest="read_from",
        help="Specify where to read from, in case of csv specify full or relative path. "
        "For API access tokens should be configured",
    )
    parser.add_argument(
        "-w", "--write-to", dest="write_to", help="Specify where to send result",
    )
    parser.add_argument(
        "-a", "--account_id", dest="account_id", help="Specify ynab account id",
    )
    parser.add_argument("-v", "--version", action="store_true", dest="show_version")
    arguments = parser.parse_args()
    return arguments


def main() -> None:
    arguments = parse_args()
    print(arguments)

    read_from = settings.READ_FROM
    write_to = settings.WRITE_TO
    source = settings.SOURCE
    account_id = settings.YNAB_ACCOUNT_ID

    # How to combine configuration file and CLI arguments,
    # Read from conf file > override form CLI args

    # default csv swedbank
    provider = SwedbankCSVProvider()
    if source == 'revolut' and read_from != 'api':
        provider = RevolutCSVProvider()

    # read
    data = provider.read_csv(input_file=read_from)

    # transform
    transformer = SwedBankTransformer(account_id=account_id)
    if source == "revolut":
        transformer = RevolutTransformer(account_id=account_id)

    data = transformer.to_ynab_transactions(data)

    if write_to == "stdout":
        for i in data:
            print(i)
    elif write_to == "api":
        yn = YnabBudget(api_key=settings.YNAB_API_KEY, budget_id=settings.YNAB_BUDGET_ID)
        yn.create_transactions(data)
    print("done")


if __name__ == "__main__":
    main()
