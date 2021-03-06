import base64
import hashlib
import hmac
import urllib
import urllib.parse

from .connection import ExchangeConnection


class KrakenConnectionError(Exception):
    pass


class KrakenConnection(ExchangeConnection):
    def __init__(self, uri='https://api.kraken.com', version='0', key=None, secret=None,
                 timeout=10):
        super().__init__(uri, version, key, secret)

    def __enter__(self):
        pass

    def __exit__(self, type_, value, traceback):
        pass

    def query(self, endpoint, sign=False, **kwargs):
        """Prepare a request for the exchange."""
        request_type = 'private' if sign else 'public'
        path = '/' + '/'.join([self.version, request_type, endpoint])

        params = kwargs['params'] if 'params' in kwargs else {}

        if sign:
            headers, params = self._sign(path, params)

        encoded_data = urllib.parse.urlencode(params)

        return self._request('POST', path, headers=headers, data=encoded_data)

    def _sign(self, path, params=None):
        if not params:
            params = {}

        params['nonce'] = self._nonce()

        post_data = urllib.parse.urlencode(params)
        encoded_data = (params['nonce'] + post_data).encode()
        message = path.encode() + hashlib.sha256(encoded_data).digest()
        signature = hmac.new(base64.b64decode(self.secret), message, hashlib.sha512)
        digest = base64.b64encode(signature.digest())

        headers = {
            'API-Key': self.key,
            'API-Sign': digest.decode(),
        }

        return headers, params
