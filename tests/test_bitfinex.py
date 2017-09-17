import logging
import logging.config
import os
import unittest

from venice.api.bitfinex import BitfinexAPI


logging.config.fileConfig('logging_tests.conf')


class TestBitfinex(unittest.TestCase):
    def test_public(self):
        api = BitfinexAPI()

        result = api.query('GET', 'symbols')
        self.assertTrue(result.ok, result.text)

    def test_public_with_arguments(self):
        api = BitfinexAPI()

        result = api.query('GET', 'stats/btcusd')
        self.assertTrue(result.ok, result.text)

    def test_private(self):
        api = BitfinexAPI()
        api.load_key(os.path.expanduser('~') + '/.bitfinex.key')

        result = api.query('POST', 'account_infos', sign=True)
        self.assertTrue(result.ok, result.text)

    def test_private_with_arguments(self):
        api = BitfinexAPI()
        api.load_key(os.path.expanduser('~') + '/.bitfinex.key')

        result = api.query('POST', 'mytrades', sign=True, params={'symbol': 'ltcusd'})
        self.assertTrue(result.ok, result.text)
