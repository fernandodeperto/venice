import logging
import logging.config
import os
import unittest

from venice.api.kraken import KrakenAPI


logging.config.fileConfig('logging_tests.conf')


class TestKraken(unittest.TestCase):
    def test_public(self):
        api = KrakenAPI()

        status_code, result = api.query('Ticker', params={'pair': 'XETHZUSD'})
        self.assertEqual(status_code, 200, result)
        self.assertFalse(len(result['error']), result['error'])

    def test_private(self):
        api = KrakenAPI()
        api.load_key(os.path.expanduser('~') + '/.kraken.key')

        status_code, result = api.query('Balance', sign=True)
        self.assertEqual(status_code, 200, result)
        self.assertFalse(len(result['error']), result['error'])

    def test_private_with_params(self):
        api = KrakenAPI()
        api.load_key(os.path.expanduser('~') + '/.kraken.key')

        status_code, result = api.query('TradeBalance', sign=True, params={'asset': 'ZEUR'})
        self.assertEqual(status_code, 200, result)
        self.assertFalse(len(result['error']), result['error'])
