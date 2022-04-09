# YNAB - You Need a Budget

[![Tests](https://github.com/demonno/ynab-import/workflows/Test%20Suite/badge.svg)](https://github.com/demonno/ynab-import/actions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![version](https://img.shields.io/pypi/v/ynab-import.svg)](https://pypi.org/project/ynab-import/)
[![license](https://img.shields.io/pypi/l/ynab-import)](https://github.com/demonno/ynab-import/blob/master/LICENSE)

Budgeting Tool helps you plan and manage your personal budget.
In Ynab you have budgets, each budget has one or more accounts with transactions.

## Install

    pip install ynab-import

## Configuration file
config.env

```ini
READER=swedbank_csv
WRITER=ynab_api
READ_FROM_PATH=...

YNAB_API_key=**********
YNAB_BUDGET_ID==**********
YNAB_ACCOUNT_ID==**********
```

## Check config

   ynab-import --config example.env check


##### Ynab API KEY
To set up API integration with YNAB you need to create `Personal Access Token`.

Go to `https://app.youneedabudget.com/settings/developer` and click `New Token`
