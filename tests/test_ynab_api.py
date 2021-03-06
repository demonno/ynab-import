from uuid import UUID

import requests_mock
from hypothesis import given
from hypothesis.strategies import builds, uuids

from ynab_import.common.models import YnabTransaction
from ynab_import.ynab.ynab_api import YnabApi


@given(transaction=builds(YnabTransaction), budget_id=uuids())
def test_it_creates_transactions(transaction, budget_id: UUID):
    with requests_mock.Mocker() as m:
        m.post(f'https://api.youneedabudget.com/v1/budgets/{budget_id}/transactions')
        YnabApi(api_key="123", budget_id=str(budget_id)).create_transactions(
            transactions=[transaction]
        )
        assert m.last_request.json() == {'transactions': [transaction.to_dict()]}