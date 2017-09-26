import base64
import hashlib
import hmac
import json

from .connection import ExchangeConnection, ExchangeConnectionException


class BitfinexConnection(ExchangeConnection):
    """Bitfinex connection class."""
    def __init__(self, uri='https://api.bitfinex.com/', version='v1', key=None, secret=None,
                 timeout=5):
        super().__init__(uri, version, key, secret)

    def query(self, method, endpoint, sign=False, **kwargs):
        """Prepare a query for the exchange."""
        path = '/'.join([self.version, endpoint])

        headers = {
            'User-Agent': 'venice/1.0'
        }

        if sign:
            headers.update(self._sign(path, kwargs['params'] if 'params' in kwargs else None))

        return self._request(method, path, headers=headers)

    def _sign(self, path, params=None):
        if not params:
            params = {}

        params['nonce'] = self._nonce()
        params['request'] = '/' + path

        encoded_params = base64.standard_b64encode(json.dumps(params).encode('utf-8'))
        hash_params = hmac.new(self.secret.encode('utf-8'), encoded_params, hashlib.sha384)

        return {
            "X-BFX-APIKEY": self.key,
            "X-BFX-SIGNATURE": hash_params.hexdigest(),
            "X-BFX-PAYLOAD": encoded_params,
        }
