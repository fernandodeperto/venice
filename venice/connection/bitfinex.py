import base64
import hashlib
import hmac
import json
import logging

from os.path import expanduser

from .connection import ExchangeConnection


class BitfinexConnection(ExchangeConnection):
    """Bitfinex connection class."""
    def __init__(self, uri='https://api.bitfinex.com/', version='v1', key=None, secret=None,
                 timeout=5):
        super().__init__(uri, version, key, secret)

        self.headers = {
            'User-Agent': 'venice/1.0'
        }

    def __enter__(self):
        self.load_key(expanduser('~') + '/.bitfinex.key')

        return self

    def query(self, method, endpoint, sign=False, **kwargs):
        """Prepare a query for the exchange."""
        path = self._path(endpoint)

        headers = self.headers

        if 'get_params' in kwargs:
            path += self._format_get_params(kwargs['get_params'])

        if sign:
            headers.update(self._sign(path, kwargs['params'] if 'params' in kwargs else None))

        return self._request(method, path, headers=headers)

    def query_public(self, endpoint, **kwargs):
        return self.query('GET', endpoint, **kwargs)

    def query_private(self, endpoint, **kwargs):
        return self.query('POST', endpoint, sign=True, **kwargs)

    def _sign(self, path, params=None):
        logger = logging.getLogger(__name__)

        if not params:
            params = {}

        params['nonce'] = self._nonce()
        params['request'] = '/' + path

        logger.debug('params={}'.format(params))

        encoded_params = base64.standard_b64encode(json.dumps(params).encode('utf-8'))
        hash_params = hmac.new(self.secret.encode('utf-8'), encoded_params, hashlib.sha384)

        return {
            "X-BFX-APIKEY": self.key,
            "X-BFX-SIGNATURE": hash_params.hexdigest(),
            "X-BFX-PAYLOAD": encoded_params,
        }
