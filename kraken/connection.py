import json
import time

import hashlib
import hmac
import base64

import http.client

import urllib.request
import urllib.parse
import urllib.error

NONCE_MULTIPLIER = 1000


class KrakenAPI:
    def __init__(self, key='', secret='', url='api.kraken.com', version='0'):
        self.key = key
        self.secret = secret
        self.url = url
        self.version = version
        self.connection = None

        self.headers = {
            'User-Agent': 'krakenapi/0.9'
        }

    def __enter__(self):
        self.connection = http.client.HTTPSConnection(self.url)
        return self

    def __exit__(self, type, value, traceback):
        self.connection.close()

    def load_key(self, path):
        with open(path, 'r') as f:
            self.key = f.readline().strip()
            self.secret = f.readline().strip()

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
        data = urllib.parse.urlencode(request)

        headers.update(self.headers)

        self.connection.request('POST', path, data, headers)
        response = self.connection.getresponse()

        return json.loads(response.read().decode())

    def _path(self, request_type, method):
        return '/' + '/'.join([self.version, request_type, method])

    def _nonce(self):
        return int(NONCE_MULTIPLIER * time.time())
