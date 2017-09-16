import base64
import hashlib
import hmac
import urllib
import urllib.parse


from .api import ExchangeAPI


class KrakenAPI(ExchangeAPI):
    """Kraken exchange API."""
    def __init__(self, uri='https://api.kraken.com/', version='0', key=None, secret=None,
                 timeout=10):
        super().__init__(uri, version, key, secret)

    def query(self, endpoint, sign=False, **kwargs):
        """Prepare a request for the exchange."""
        request_type = 'private' if sign else 'public'
        path = '/'.join([self.version, request_type, endpoint])

        headers = {
            'User-Agent': 'venice/1.0'
        }

        if sign:
            headers.update(self._sign(path, kwargs['params'] if 'params' in kwargs else None))

        return self._request('POST', path, headers=headers)

    def _sign(self, path, params=None):
        if not params:
            params = {}

        params['nonce'] = self._nonce()

        query_data = urllib.parse.urlencode(params)
        encoded_data = (params['nonce'] + query_data).encode('utf-8')
        message = path.encode('utf-8') + hashlib.sha256(encoded_data).digest()
        signature = hmac.new(base64.b64decode(self.secret), message, hashlib.sha512)
        digest = base64.b64encode(signature.digest())

        return {
            'API-Key': self.key,
            'API-Sign': digest.decode('utf-8')
        }
