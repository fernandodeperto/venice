import abc
import json
import logging
import requests
import time


class ExchangeConnectionException(Exception):
    pass


class ExchangeConnection(metaclass=abc.ABCMeta):
    """
    Base class for Exchange connection."""
    def __init__(self, uri, version=None, key=None, secret=None, timeout=5):
        """Create ExchangeConnection object."""
        self.uri = uri
        self.version = version
        self.key = key
        self.secret = secret
        self.timeout = timeout

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        pass

    def load_key(self, path):
        """Load key and secret from file."""
        with open(path, 'r') as f:
            self.key = f.readline().strip()
            self.secret = f.readline().strip()

    @abc.abstractmethod
    def query(self, method, endpoint, sign=False, **kwargs):
        """Abstract method used to send the request to the exchange."""
        raise NotImplementedError

    def query_public(self, endpoint, **kwargs):
        """Make a public request to the exchange."""
        raise NotImplementedError

    def query_private(self, endpoint, **kwargs):
        """Make a private request to the exchange."""
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
            'new request: method={}, path={}, kwargs={}, ok={}, status_code={}, text={}'.format(
                method, path, kwargs, response.ok, response.status_code, response.text))

        return response.ok, json.loads(response.text) if response.ok else None

    @staticmethod
    def _format_get_params(params):
        return '?' + '&'.join(['{}={}'.format(x, params[x]) for x in params])

    def _path(self, endpoint):
        return '/'.join([self.version, endpoint])
