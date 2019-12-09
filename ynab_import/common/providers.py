from typing import List

import requests

from ynab_import.common.models import YnabTransaction
from ynab_import.common import settings


class BaseProvider(object):
    pass


class CSVProvider(BaseProvider):
    """Reading data from csv files"""

    def read_csv(self, input_file: str):
        raise NotImplemented


class APIProvider(BaseProvider):
    """Fetching/Submitting data using APIs"""

    pass
