import datetime

from ynab_import.core.interactions import Transaction
from ynab_import.infra.tbc.providers import TBCCSVReader


def test_read_transaction_data_from_csv():
    reader = TBCCSVReader(source_file_path="data/tbc.csv", exchange_rate=2.9112)
    transactions = reader.read_transactions()

    assert len(transactions) == 7
    assert transactions[0] == Transaction(
        date=datetime.datetime(2024, 3, 28, 0, 0),
        description="POS wallet - Agrohub (universiteti),  თანხა 52.65 GEL, Mar 26 2024 10:31AM,  რესტორანი, კაფე, ბარი",
        amount=-18085,
        payee_name="თიბისი ბანკის MC ბარათებით სავაჭრო ობიექტებში სხვა ბანკის ტერმინალებში",
    )
    assert transactions[1] == Transaction(
        date=datetime.datetime(2024, 3, 27, 0, 0),
        description="პირადი გადარიცხვა",
        amount=17175,
        payee_name="ჯეინ დო, 0000000000",
    )
    assert transactions[2] == Transaction(
        date=datetime.datetime(2024, 3, 25, 0, 0),
        description="Private transfer within TBC",
        amount=-68700,
        payee_name="ჯეინ დო",
    )
    assert transactions[3] == Transaction(
        date=datetime.datetime(2024, 3, 23, 0, 0),
        description="Geocell;555555555;თანხა:5.00",
        amount=-1717,
        payee_name="გადარიცხვების სატრანზიტო ანგარიში - ჯეოსელი",
    )
