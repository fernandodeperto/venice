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


class KrakenConnectionError(Exception):
    pass


class KrakenAPI(ExchangeAPI):
    def __init__(self, uri='api.kraken.com', version='0', key=None, secret=None,
                 timeout=10):
        super().__init__(uri, version, key, secret)

    def query(self, endpoint, sign=False, **kwargs):
        request = kwargs['params'] if 'params' in kwargs else {}

        self.connect()

        if sign:
            result = self.query_private(endpoint, request)
        else:
            result = self.query_public(endpoint, request)

        self.disconnect()
        return 200, result

    def connect(self):
        self.connection = http.client.HTTPSConnection(self.uri)
        return self

    def disconnect(self):
        self.connection.close()

    def query_public(self, method, request={}):
        path = '/' + '/'.join([self.version, 'public', method])
        return self._query(path, request)

    def query_private(self, method, request={}):
        path = '/' + '/'.join([self.version, 'private', method])

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
        headers.update({
            'User-Agent': 'venice/1.0'
        })

        try:
            self.connection.request('POST', path, data, headers)

            response = self.connection.getresponse()
            result = json.loads(response.read().decode())
        except:
            raise KrakenConnectionError

        logger.debug(result)

        return result

    def _nonce(self):
        return int(1000 * time.time())


