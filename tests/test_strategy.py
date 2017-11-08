import logging
import logging.config
import time
import unittest

from decimal import Decimal

from venice.api.bitfinex import BitfinexAPI
from venice.strategy import StrategyAPI


class TestStrategyAPI(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        logging.config.fileConfig('logging_tests.conf')

        self.pair = 'ltcusd'
        self.period = '15'
        self.capital = 7
        self.comission = 0.001

        self.api = StrategyAPI(
            BitfinexAPI(), self.pair, self.period, self.capital, comission=self.comission)

    def setUp(self):
        time.sleep(5)

    def test_close(self):
        logger = logging.getLogger(__name__)

        result = self.api.close()
        logger.debug(result)
        self.assertIsNotNone(result)

    def test_high(self):
        logger = logging.getLogger(__name__)

        result = self.api.high()
        logger.debug(result)
        self.assertIsNotNone(result)

    def test_hl2(self):
        logger = logging.getLogger(__name__)

        result = self.api.hl2()
        logger.debug(result)
        self.assertIsNotNone(result)

    def test_hlc3(self):
        logger = logging.getLogger(__name__)

        result = self.api.hlc3()
        logger.debug(result)
        self.assertIsNotNone(result)

    def test_low(self):
        logger = logging.getLogger(__name__)

        result = self.api.low()
        logger.debug(result)
        self.assertIsNotNone(result)

    def test_ohl4(self):
        logger = logging.getLogger(__name__)

        result = self.api.ohl4()
        logger.debug(result)
        self.assertIsNotNone(result)

    def test_ohlc(self):
        logger = logging.getLogger(__name__)

        result = self.api.ohlc()
        logger.debug(result)
        self.assertIsNotNone(result)

    def test_open(self):
        logger = logging.getLogger(__name__)

        result = self.api.open()
        logger.debug(result)
        self.assertIsNotNone(result)

    def test_ticker(self):
        logger = logging.getLogger(__name__)

        result = self.api.ticker()
        logger.debug(result)
        self.assertIsNotNone(result)

    def test_market_order(self):
        logger = logging.getLogger(__name__)

        result = self.api.order_buy('TestOrder', Decimal.from_float(0.2))
        logger.debug(result)
        self.assertIsNotNone(result)

        time.sleep(5)

        self.api.update()

        result = self.api.order_sell('TestOrder')
        logger.debug(result)
        self.assertIsNotNone(result)
