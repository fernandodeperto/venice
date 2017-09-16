import os
import unittest

from venice.api.bitfinex import BitfinexAPI


class TestBitfinex(unittest.TestCase):
    def test_public(self):
        api = BitfinexAPI()

        result = api.request('GET', 'symbols')
        self.assertTrue(result.ok, result.text)

    def test_public_with_arguments(self):
        api = BitfinexAPI()

        result = api.request('GET', 'stats/btcusd')
        self.assertTrue(result.ok, result.text)

    def test_private(self):
        api = BitfinexAPI()
        api.load_key(os.path.expanduser('~') + '/.bitfinex.key')

        result = api.request('POST', 'account_infos', sign=True)
        self.assertTrue(result.ok, result.text)

    def test_private_with_arguments(self):
        api = BitfinexAPI()
        api.load_key(os.path.expanduser('~') + '/.bitfinex.key')

        result = api.request('POST', 'mytrades', sign=True, params={'symbol': 'ltcusd'})
        self.assertTrue(result.ok, result.text)
