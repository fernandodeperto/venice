import abc
import time


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

    @staticmethod
    def nonce():
        """Create a nonce based on the current time."""
        return str(int(1000 * time.time()))

    @abc.abstractmethod
    def request(self, method, endpoint, sign=False, params=None):
        """Abstract method used to send the request to the exchange."""
        raise NotImplementedError
