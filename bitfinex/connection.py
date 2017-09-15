import hashlib
import hmac
import json
import requests
import time

NONCE_MULTIPLIER = 1000


class BitfinexConnectionError(Exception):
    pass


class BitfinexConnection:
    def __init__(self, base_url='api.bitfinex.com', version='v1', key='', secret=''):
        self.base_url = base_url
        self.version = version
        self.key = key
        self.secret = secret

    def _nonce(self):
        """
        Returns a nonce
        Used in authentication
        """
        return str(int(round(time.time() * 10000)))

    def _headers(self, path, nonce, body):
        signature = '/api/' + path + nonce + body

        h = hmac.new(
            bytes(self.secret, 'latin-1'),
            bytes(signature, 'latin-1'),
            hashlib.sha384)

        signature = h.hexdigest()

        return {
            'bfx-nonce': nonce,
            'x-bfx-apikey': self.key,
            'bfx-signature': signature,
            'content-type': 'application/json'
        }

    def req(self, path, params={}):
        nonce = self._nonce()
        body = json.dumps(params)
        headers = self._headers(path, nonce, body)
        print(headers)
        url = 'https://' + self.base_url + '/' + self.version + '/' + path
        print(url)
        result = requests.post(url, headers=headers, data=body, verify=True)
        return result

    def active_orders(self):
        """
        Fetch active orders
        """
        response = self.req('orders')
        if response.status_code == 200:
            return response.json()
        else:
            print(response.status_code)
            print(response)
            return ''

    def orders_history(self, limit=10):
        """
        Fetch orders history
        """
        params = {'limit': str(limit)}
        response = self.req('orders/hist', params)
        if response.status_code == 200:
            return response.json()
        else:
            print(response.status_code)
            print(response)
            return ''

    def key_info(self):
        response = self.req('key_info')
        print(response.json())
        print(response.status_code)
        print(response)
        return ''
