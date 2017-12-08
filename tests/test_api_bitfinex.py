import logging
import logging.config
import time
import unittest

from  decimal import Decimal

from venice.api.bitfinex import BitfinexAPI
from venice.api.api import ExchangeAPI

logging.config.fileConfig('logging_tests.conf')


class TestBitfinexAPI(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.api = BitfinexAPI()

    def setUp(self):
        time.sleep(5)

    def test_ticker(self):
        logger = logging.getLogger(__name__)

        result = self.api.ticker(ExchangeAPI.LTCUSD)
        logger.debug(result)
        self.assertIsNotNone(result)

    def test_ohlc(self):
        logger = logging.getLogger(__name__)

        result = self.api.ohlc(ExchangeAPI.LTCUSD, ExchangeAPI.P15, limit=5)
        logger.debug(result)
        self.assertIsNotNone(result)

    def test_order(self):
        logger = logging.getLogger(__name__)

        result = self.api.add_order(
            ExchangeAPI.LTCUSD, ExchangeAPI.BUY, ExchangeAPI.LIMIT, Decimal('0.2'), price=20)
        logger.debug(result)
        self.assertIsNotNone(result)

        result = self.api._cancel_orders([x.id_ for x in result])
        logger.debug(result)
        self.assertIsNotNone(result)

    def test_active_orders(self):
        logger = logging.getLogger(__name__)

        result = self.api.order_history(ExchangeAPI.BTCUSD)
        logger.debug(result)
        self.assertIsNotNone(result)

    def test_order_history(self):
        logger = logging.getLogger(__name__)

        result = self.api.order_history(limit=2)
        logger.debug(result)
        self.assertIsNotNone(result)

    def test_order_status(self):
        logger = logging.getLogger(__name__)

        id_ = 4289014289
        result = self.api.order_status(id_)
        logger.debug(result)
        self.assertIsNotNone(result)

    def test_balance(self):
        logger = logging.getLogger(__name__)

        result = self.api.balance()
        logger.debug(result)
        self.assertIsNotNone(result)

    def test_pairs(self):
        logger = logging.getLogger(__name__)

        result = self.api.pairs
        logger.debug(result)
        self.assertIsNotNone(result)

    def test_fees(self):
        logger = logging.getLogger(__name__)

        maker_fee, taker_fee = self.api.fees()

        logger.debug(maker_fee)
        self.assertIsNotNone(maker_fee)

        logger.debug(taker_fee)
        self.assertIsNotNone(taker_fee)
