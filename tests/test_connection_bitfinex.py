import logging
import logging.config
import os
import unittest

from venice.connection import ExchangeConnectionException
from venice.connection.bitfinex import BitfinexConnection

logging.config.fileConfig('logging_tests.conf')


class TestBitfinexConnection(unittest.TestCase):
    def test_exception(self):
        with self.assertRaises(ExchangeConnectionException):
            with BitfinexConnection() as c:
                c.query('GET', 'stats/btcbtc')

    def test_public(self):
        with BitfinexConnection() as c:
            result = c.query('GET', 'symbols')
            self.assertIsNotNone(result)

    def test_public_with_arguments(self):
        with BitfinexConnection() as c:
            result = c.query('GET', 'stats/btcusd')
            self.assertIsNotNone(result)

    def test_private(self):
        with BitfinexConnection() as c:
            result = c.query('POST', 'account_infos', sign=True)
            self.assertIsNotNone(result)

    def test_private_with_arguments(self):
        with BitfinexConnection() as c:
            result = c.query('POST', 'mytrades', sign=True, params={'symbol': 'ltcusd'})
            self.assertIsNotNone(result)
