import base64
import hashlib
import hmac
import json
import logging
import urllib
import urllib.parse

import requests

from .api import ExchangeAPI


class KrakenAPI(ExchangeAPI):
    """Kraken exchange API."""
    def __init__(self, uri='https://api.kraken.com/', version='0', key=None, secret=None,
                 timeout=10):
        super().__init__(uri, version, key, secret)

        self.logger = logging.getLogger(__name__)
        print(__name__)

    def request(self, endpoint, sign=False, params=None):
        """Prepare and send a request for the exchange."""
        request_type = 'private' if sign else 'public'
        path = '/'.join([self.version, request_type, endpoint])

        headers = {
            'User-Agent': 'venice/1.0'
        }

        if sign:
            if not params:
                params = {}

            params['nonce'] = self.nonce()

            query_data = urllib.parse.urlencode(params)
            encoded_data = (params['nonce'] + query_data).encode('utf-8')
            message = path.encode('utf-8') + hashlib.sha256(encoded_data).digest()
            signature = hmac.new(base64.b64decode(self.secret), message, hashlib.sha512)
            digest = base64.b64encode(signature.digest())

            headers.update({
                'API-Key': self.key,
                'API-Sign': digest.decode('utf-8')
            })

        self.logger.debug('New request: path: %s, headers: %s, params: %s', self.uri +
                          path, headers, params)

        return requests.request('POST', self.uri + path, timeout=self.timeout, headers=headers,
                                json=params)
