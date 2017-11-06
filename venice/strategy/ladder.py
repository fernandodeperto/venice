from decimal import Decimal
from logging import getLogger
from collections import namedtuple

# from venice.util import EPSILON
from .strategy import Strategy

LadderOrder = namedtuple('Order', 'name, price, step')


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
        parser.add_argument('-b', '--buy', type=int, help='buy some steps at start')
        parser.add_argument('steps', type=int, help='Number of order steps')
        parser.add_argument('stop', type=float, help='Trailing stop value for orders')

    def run(self):
        logger = getLogger(__name__)

        ticker = self.api.ticker()
        self.pivot = max(self.pivot, ticker.last)

        while self.orders and ticker.last >= self.orders[-1].price + self.stop:
            logger.info('closed sell order @ {}: {}'.format(ticker.last, self.orders.pop()))

        if len(self.orders) < self.steps and ticker.last <= self.pivot - self.stop:
            order_name = 'Ladder' + str(len(self.orders))
            # volume = self.api.capital / self.steps / ticker.last

            # self.api.order_buy(order_name, volume=volume)
            # self.api.order_sell(order_name, limit=ticker.last + self.stop)

            self.orders.append(LadderOrder(order_name, ticker.last, self.steps))

            self.pivot = ticker.last

            logger.info('closed buy order @ {}: {}'.format(ticker.last, self.orders[-1]))

        logger.info('last={:.5f}, pivot={:.5f}, orders={}'.format(
            ticker.last, self.pivot, self.orders))

    def clean_up(self):
        pass
