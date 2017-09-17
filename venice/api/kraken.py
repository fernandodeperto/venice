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

    def query2(self, endpoint, sign=False, **kwargs):
        logger = logging.getLogger(__name__)

        request = kwargs['params'] if 'params' in kwargs else {}

        if sign:
            result = self.query_private(endpoint, request)
        else:
            result = self.query_public(endpoint, request)

        result_json = json.loads(result.text)

        logger.debug(result_json)

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
