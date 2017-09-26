import logging
import logging.config
import os
import unittest

from venice.api.bitfinex import BitfinexAPI


logging.config.fileConfig('logging_tests.conf')


class TestBitfinexAPI(unittest.TestCase):
    def test_ticker(self):
        with BitfinexAPI() as api:
            code, text  = api.ticker('ltcusd')
