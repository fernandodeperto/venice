import os
import unittest

from venice.api.kraken import KrakenAPI


class TestKraken(unittest.TestCase):
    def test_public(self):
        api = KrakenAPI()

        result = api.query('Ticker', params={'pair': 'XETHZUSD'})
        self.assertTrue(result.ok, result.text)

    def test_private(self):
        api = KrakenAPI()
        api.load_key(os.path.expanduser('~') + '/.kraken.key')

        result = api.query('TradeBalance', sign=True, params={'asset': 'ZEUR'})
        self.assertTrue(result.ok, result.text)
