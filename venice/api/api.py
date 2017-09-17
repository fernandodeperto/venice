import abc
import json
import logging
import requests
import time


class ExchangeConnectionException(Exception):
    pass


class ExchangeAPI(metaclass=abc.ABCMeta):
    """
    Base class for Exchange APIs."""
    def __init__(self, uri, version=None, key=None, secret=None, timeout=5):
        """Create ExchangeAPI object."""
        self.uri = uri
        self.version = version
        self.key = key
        self.secret = secret
        self.timeout = timeout

    def load_key(self, path):
        """Load key and secret from file."""
        with open(path, 'r') as f:
            self.key = f.readline().strip()
            self.secret = f.readline().strip()

    @abc.abstractmethod
    def query(self, method, endpoint, sign=False, **kwargs):
        """Abstract method used to send the request to the exchange."""
        raise NotImplementedError

    @staticmethod
    def _nonce():
        """Create a nonce based on the current time."""
        return str(int(1000 * time.time()))

    def _request(self, method, path, **kwargs):
        """Send the resquest to the exchange."""
        logger = logging.getLogger(__name__)

        response = requests.request(method, self.uri + path, timeout=self.timeout, **kwargs)

        logger.debug(
            'new request: method={}, path={}, kwargs={}, ok={}, text={}'.format(
                method, path, kwargs, response.ok, response.text))

        return response.status_code, json.loads(response.text)
