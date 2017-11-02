import logging

from decimal import Decimal

from .strategy import Strategy


class TrailingStrategy(Strategy):
    def __init__(self, api, stop, *args, **kwargs):
        super().__init__(api, *args, **kwargs)

        logger = logging.getLogger(__name__)

        self.stop = Decimal.from_float(stop)

        ohlc = self.api.ohlc(limit=1)
        self.pivot = ohlc[-1].close

        self.buy = True

        logger.info('trailing stop started with stop={} and pivot={}'.format(
            self.stop, self.pivot))

    @staticmethod
    def descr_text():
        return 'Trailing stop strategy'

    @staticmethod
    def help_text():
        return 'Trailing stop strategy'

    @staticmethod
    def configure_parser(parser):
        parser.add_argument('stop', type=float, help='Trailing stop value for orders')

    def run(self):
        logger = logging.getLogger(__name__)

        ticker = self.api.ticker()

        if self.buy:
            self.pivot = min(self.pivot, ticker.last)

            if ticker.last > self.pivot + self.stop:
                logger.info('buy order')
                self.buy = False

        else:
            self.pivot = max(self.pivot, ticker.last)

            if ticker.last < self.pivot - self.stop:
                logger.info('sell order')
                self.buy = True

        logger.info('last={:.5f}, pivot={:.5f}, stop={:.5f}, buy={}'.format(
            ticker.last, self.pivot, self.stop, self.buy))

    def clean_up(self):
        pass
