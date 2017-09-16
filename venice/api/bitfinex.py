import base64
import hashlib
import hmac
import json

import requests

from .api import ExchangeAPI


class BitfinexAPI(ExchangeAPI):
    """Bitfinex API class."""
    def __init__(self, uri='https://api.bitfinex.com/', version='v1', key=None, secret=None,
                 timeout=5):
        super().__init__(uri, version, key, secret)

    def request(self, method, endpoint, sign=False, params=None):
        """Prepare and send a query for the exchange."""
        path = self.version + '/' + endpoint if self.version else endpoint

        headers = {
            'User-Agent': 'venice/1.0'
        }

        if sign:
            if not params:
                params = {}

            params['nonce'] = self.nonce()
            params['request'] = '/' + self.version + '/' + endpoint

            encoded_params = base64.standard_b64encode(json.dumps(params).encode('utf-8'))
            hash_params = hmac.new(self.secret.encode('utf-8'), encoded_params, hashlib.sha384)

            headers.update({
                "X-BFX-APIKEY": self.key,
                "X-BFX-SIGNATURE": hash_params.hexdigest(),
                "X-BFX-PAYLOAD": encoded_params,
            })

        return requests.request(method, self.uri + path, timeout=self.timeout, headers=headers)
