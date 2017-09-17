import base64
import hashlib
import hmac
import requests
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
    def __init__(self, uri='https://api.kraken.com', version='0', key=None, secret=None,
                 timeout=10):
        super().__init__(uri, version, key, secret)

    def query(self, endpoint, sign=False, **kwargs):
        request = kwargs['params'] if 'params' in kwargs else {}

        if sign:
            result = self.query_private(endpoint, request)
        else:
            result = self.query_public(endpoint, request)

        result_json = json.loads(result.text)

        return result.status_code, result_json

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

        return requests.request('POST', self.uri + path, headers=headers, data=data)

    def _nonce(self):
        return int(1000 * time.time())
