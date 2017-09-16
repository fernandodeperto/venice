import logging
import os
import unittest

from venice.api.kraken import KrakenAPI


class TestKraken(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

    def test_public(self):
        api = KrakenAPI()

        result = api.request('Ticker', params={'pair': 'XETHZUSD'})
        self.assertTrue(result.ok, result.text)

    def test_private(self):
        api = KrakenAPI()
        api.load_key(os.path.expanduser('~') + '/.kraken.key')

        result = api.request('TradeBalance', sign=True, params={'asset': 'ZEUR'})
        self.assertTrue(result.ok, result.text)
