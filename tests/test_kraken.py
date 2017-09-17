import logging
import logging.config
import os
import unittest

from venice.api.kraken import KrakenAPI


logging.config.fileConfig('logging_tests.conf')


class TestKraken(unittest.TestCase):
    def test_public(self):
        logger = logging.getLogger(__name__)

        api = KrakenAPI()

        result = api.query('Ticker', params={'pair': 'XETHZUSD'})
        self.assertTrue(result.ok, result.text)

        logger.debug(result.text)

    def test_private(self):
        logger = logging.getLogger(__name__)

        api = KrakenAPI()
        api.load_key(os.path.expanduser('~') + '/.kraken.key')

        result = api.query('TradeBalance', sign=True, params={'asset': 'ZEUR'})
        self.assertTrue(result.ok, result.text)

        logger.debug(result.text)
