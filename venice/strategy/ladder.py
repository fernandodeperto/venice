from decimal import Decimal
from logging import getLogger

# from venice.util import EPSILON
from .strategy import Strategy


class LadderStrategy(Strategy):
    def __init__(self, api, steps, stop, *args, **kwargs):
        super().__init__(api, *args, **kwargs)

        logger = getLogger(__name__)

        self.steps = steps
        self.stop = Decimal.from_float(stop)

        ohlc = self.api.ohlc(limit=1)
        self.pivot = ohlc[-1].close

        logger.info('ladder strategy started with {} steps, stop={:.5f}, pivot={:.5f}'.format(
            self.steps, self.stop, self.pivot))

        self.orders = []

    @staticmethod
    def descr_text():
        return 'Ladder strategy'

    @staticmethod
    def help_text():
        return 'Ladder strategy'

    @staticmethod
    def configure_parser(parser):
        parser.add_argument('steps', type=int, help='Number of order steps')
        parser.add_argument('stop', type=float, help='Trailing stop value for orders')

    def run(self):
        logger = getLogger(__name__)

        ticker = self.api.ticker()

        self.pivot = max(self.pivot, ticker.last)

        if self.steps and self.pivot - ticker.last > self.stop:
            self.pivot = ticker.last
            self.orders.append((self.steps, ticker.last))

            logger.info('buy order {} @ {}'.format(self.steps, ticker.last))

            self.steps -= 1

        if self.orders and ticker.last >= self.orders[-1][1]:
            step, price = self.orders.pop()

            logger.info('sell order {} @ {}'.format(step, ticker.last))

        logger.info('last={:.5f}, pivot={:.5f}, steps={}, orders={}'.format(
            ticker.last, self.pivot, self.steps, self.orders))

    def clean_up(self):
        pass
