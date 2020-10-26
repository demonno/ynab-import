class BaseProvider(object):
    pass


class CSVProvider(BaseProvider):
    """Reading data from csv files"""

    def read_csv(self, input_file: str):
        raise NotImplementedError


class APIProvider(BaseProvider):
    """Fetching/Submitting data using APIs"""

    pass
