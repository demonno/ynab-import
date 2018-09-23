import csv

YNAB_COLUMNS = ['Date', 'Payee', 'Memo', 'OUTFLOW', 'INFLOW']

with open('swedbank.csv', 'r', encoding='utf8') as f:
    csv_reader = csv.reader(f, delimiter=';', quotechar='"')
    csswedbank_data = list(csv_reader)
swedbank_headers, swedbank_rows = csswedbank_data[0], csswedbank_data[1:]

client_account = swedbank_headers.index('Client account')
date = swedbank_headers.index('Date')
payee = swedbank_headers.index('Beneficiary/Payer')
memo = swedbank_headers.index('Details')
amount = swedbank_headers.index('Amount')
debit_credit = swedbank_headers.index('Debit/Credit')

with open('ynab.csv', 'w', encoding='utf8') as ynab_csv_f:
    ynab_writer = csv.writer(ynab_csv_f, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
    ynab_writer.writerow(YNAB_COLUMNS)
    for row in swedbank_rows:
        if row[memo] in ['closing balance', 'Turnover', 'Opening balance']:
            continue
        ynab_writer.writerow(
            [
                row[date],
                row[payee],
                row[memo],
                row[amount] if row[debit_credit] == 'D' else 0, # OUTFLOW
                row[amount] if row[debit_credit] == 'K' else 0  # INFLOW
            ]
        )

