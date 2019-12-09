import datetime

from ynab_import.swedbank.models import SwedbankTransaction
from ynab_import.swedbank.providers import SwedbankCSVProvider


def test_csv_provider():
    sw = SwedbankCSVProvider()
    data = sw.read_csv("tests/swedbank/swedbank.csv")
    assert len(data) == 8
    assert data[0] == SwedbankTransaction(
        client_account="EE000000000000000000",
        date=datetime.datetime(2018, 9, 4, 0, 0),
        memo="Opening balance",
        amount="1000,00",
        debit_credit="K",
        payee="",
    )
    assert data[1] == SwedbankTransaction(
        client_account="EE000000000000000000",
        date=datetime.datetime(2018, 9, 4, 0, 0),
        memo="Invoice No: 0000000000",
        amount="20,00",
        debit_credit="D",
        payee="EESTI ENERGIA AS",
    )
    assert data[2] == SwedbankTransaction(
        client_account="EE000000000000000000",
        date=datetime.datetime(2018, 9, 5, 0, 0),
        memo="Invoice No: 00000000",
        amount="50,00",
        debit_credit="D",
        payee="MY FITNESS AS",
    )
    assert data[3] == SwedbankTransaction(
        client_account="EE000000000000000000",
        date=datetime.datetime(2018, 9, 5, 0, 0),
        memo="Internet payment",
        amount="30,00",
        debit_credit="D",
        payee="TELIA EESTI AS",
    )
    # todo assert other rows
