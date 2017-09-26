import logging
import logging.config
import os
import unittest

from venice.exchange.bitfinex import BitfinexAPI


logging.config.fileConfig('logging_tests.conf')


class TestBitfinex(unittest.TestCase):
    def test_public(self):
        api = BitfinexAPI()

        status_code, result = api.query('GET', 'symbols')

        self.assertEqual(status_code, 200, status_code)

    def test_public_with_arguments(self):
        api = BitfinexAPI()

        status_code, result = api.query('GET', 'stats/btcusd')

        self.assertEqual(status_code, 200, status_code)

    def test_private(self):
        api = BitfinexAPI()
        api.load_key(os.path.expanduser('~') + '/.bitfinex.key')

        status_code, result = api.query('POST', 'account_infos', sign=True)

        self.assertEqual(status_code, 200, status_code)

    def test_private_with_arguments(self):
        api = BitfinexAPI()
        api.load_key(os.path.expanduser('~') + '/.bitfinex.key')

        status_code, result = api.query('POST', 'mytrades', sign=True, params={'symbol': 'ltcusd'})

        self.assertEqual(status_code, 200, status_code)
