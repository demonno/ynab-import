import uuid

import pytest

from ynab_import.common.transformers import Transformer

@pytest.mark.skip("Disable refactoring is done")
def test_base_transformer_amount():
    tr = Transformer(account_id=str(uuid.uuid4()))
    ynab_amount = tr.ynab_amount("10.234")
    assert ynab_amount == 10234

    ynab_amount = tr.ynab_amount("-10.234")
    assert ynab_amount == -10234

    ynab_amount = tr.ynab_amount("10.040")
    assert ynab_amount == 10040

    ynab_amount = tr.ynab_amount("010.234")
    assert ynab_amount == 10234
