import argparse
from typing import Dict, Any

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
        required=True,
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
        "-w", "--write-to", dest="write_to", help="Specify where to output from",
    )
    parser.add_argument("-v", "--version", action="store_true", dest="show_version")
    arguments = parser.parse_args()
    return arguments


def main() -> None:
    arguments = parse_args()
    print(arguments)
    read_from = arguments.read_from
    write_to = arguments.write_to
    source = arguments.source
    sw = SwedbankCSVProvider()
    data = sw.read_csv(read_from)
    tr = SwedBankTransformer()
    data = tr.to_ynab_transactions(data)
    if write_to == "stdout":
        for i in data:
            print(i)
    elif write_to == "api":
        yn = YnabBudget()
        yn.create_transactions(data)
    print("done")


if __name__ == "__main__":
    main()
