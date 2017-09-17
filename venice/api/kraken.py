import base64
import hashlib
import hmac
import urllib
import urllib.parse

import http.client
import logging
import json
import time


from .api import ExchangeAPI


class KrakenAPI(ExchangeAPI):
    """Kraken exchange API."""
    def __init__(self, uri='https://api.kraken.com/', version='0', key=None, secret=None,
                 timeout=10):
        super().__init__(uri, version, key, secret)

    def query(self, endpoint, sign=False, **kwargs):
        """Prepare a request for the exchange."""
        params = kwargs['params'] if 'params' in kwargs else {}

        with KrakenConnection(
            key='y7/AJSg0GrK2UVHeqrkQOYy/VSpNq0v7/xLYhHIxKToGrd2M+xuQwnlU',
            secret='IUSb0V6HHeYaNdiE2uSF6Eqn7NraCG6d01Ju9OGyJ2f9DgYisJZQlqcISL+sjxzD2r+WtNkVnbQ+WGFPw58p4Q==',
        ) as k:
            if sign:
                result = k.query_private(endpoint, params)
            else:
                result = k.query_public(endpoint, params)

        return 200, result


class KrakenConnectionError(Exception):
    pass


class KrakenConnection:
    def __init__(self, key='', secret='', url='api.kraken.com', version='0'):
        self.key = key
        self.secret = secret
        self.url = url
        self.version = version

        self.headers = {
            'User-Agent': 'krakenapi/0.9'
        }

    def __enter__(self):
        self.connection = http.client.HTTPSConnection(self.url)
        return self

    def __exit__(self, type, value, traceback):
        self.connection.close()

    def query_public(self, method, request={}):
        path = self._path('public', method)
        return self._query(path, request)

    def query_private(self, method, request={}):
        path = self._path('private', method)

        request['nonce'] = self._nonce()

        post_data = (str(request['nonce']) + urllib.parse.urlencode(request)).encode()

        message = path.encode() + hashlib.sha256(post_data).digest()
        signature = hmac.new(base64.b64decode(self.secret), message, hashlib.sha512)
        digest = base64.b64encode(signature.digest())

        headers = {
            'API-Key': self.key,
            'API-Sign': digest.decode()
        }

        return self._query(path, request, headers)

    def _query(self, path, request={}, headers={}):
        logger = logging.getLogger(__name__)

        logger.debug('%s: %s', path, request)

        data = urllib.parse.urlencode(request)
        headers.update(self.headers)

        try:
            self.connection.request('POST', path, data, headers)

            response = self.connection.getresponse()
            result = json.loads(response.read().decode())
        except:
            raise KrakenConnectionError

        logger.debug(result)

        return result

    def _path(self, request_type, method):
        return '/' + '/'.join([self.version, request_type, method])

    def _nonce(self):
        return int(1000 * time.time())


