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
        # TODO Add option to buy some steps at the beginning

        parser.add_argument('steps', type=int, help='Number of order steps')
        parser.add_argument('stop', type=float, help='Trailing stop value for orders')

    def run(self):
        logger = getLogger(__name__)

        ticker = self.api.ticker()
        self.pivot = max(self.pivot, ticker.last)

        order_name = 'Ladder' + str(self.steps)

        if self.steps and ticker.last <= self.pivot - self.stop:
            self.api.order_buy(order_name, volume=self.step_volume)
            self.api.order_sell(order_name, volume=self.step_volume, limit=ticker.last + self.stop)

            self.orders.append(LadderOrder(order_name, ticker.last, self.steps))

            self.pivot = ticker.last
            self.steps -= 1

        # elif self.orders and ticker.last >= self.orders[-1].price + self.stop:
        #     order = self.oprders.pop()

        #     logger.info('sell order {} @ {}'.format(step, ticker.last))

        #     self.steps += 1

        logger.info('last={:.5f}, pivot={:.5f}, steps={}, orders={}'.format(
            ticker.last, self.pivot, self.steps, self.orders))

    def clean_up(self):
        pass
