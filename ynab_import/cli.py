import click

from ynab_import.revolut.providers import RevolutCSVProvider
from ynab_import.revolut.transformers import RevolutTransformer
from ynab_import.swedbank.providers import SwedbankCSVProvider
from ynab_import.swedbank.transformers import SwedBankTransformer
from ynab_import.ynab.providers import YnabBudget


@click.command()
@click.option("--source", envvar="SOURCE", type=click.Choice(["swedbank", "revolut"]))
@click.option("--read-from", envvar="READ_FROM")
@click.option(
    "--write-to", envvar="WRITE_TO", default="api", type=click.Choice(["stdout", "api"])
)
@click.option("--account-id", envvar="YNAB_ACCOUNT_ID")
@click.option("--budget-id", envvar="YNAB_BUDGET_ID")
@click.option("--api-key", envvar="YNAB_API_KEY")
def main(source, read_from, write_to, account_id, budget_id, api_key):
    # default csv swedbank
    provider = SwedbankCSVProvider()
    if source == "revolut" and read_from != "api":
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
        yn = YnabBudget(api_key=api_key, budget_id=budget_id)
        yn.create_transactions(data)
    print("done")
