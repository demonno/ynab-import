import datetime

from ynab_import.core.interactions import Transaction
from ynab_import.swedbank.providers import SwedbankCSVReader


def test_read_transaction_data_from_csv():
    sw = SwedbankCSVReader(source_file_path="tests/swedbank/data/swedbank.csv")
    transactions = sw.read_transactions()
    assert len(transactions) == 4
    assert transactions[0] == Transaction(
        date=datetime.datetime(2018, 9, 4, 0, 0),
        description="Invoice No: 0000000000",
        amount=-20000,
        payee_name="EESTI ENERGIA AS",
    )
    assert transactions[1] == Transaction(
        date=datetime.datetime(2018, 9, 5, 0, 0),
        description="Invoice No: 00000000",
        amount=-50000,
        payee_name="MY FITNESS AS",
    )
    assert transactions[2] == Transaction(
        date=datetime.datetime(2018, 9, 5, 0, 0),
        description="Internet payment",
        amount=-30000,
        payee_name="TELIA EESTI AS",
    )
    assert transactions[3] == Transaction(
        date=datetime.datetime(2018, 9, 5, 0, 0),
        description="Private Payment",
        amount=50000,
        payee_name="John Doe",
    )
