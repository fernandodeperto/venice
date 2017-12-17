import re

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

        self.orders = []
        self.pending_order = None

        self.pivot = -1
        self.steps = steps
        self.stop = Decimal.from_float(stop)
        self.correction = Decimal.from_float(0.5)

        logger.info('ladder strategy started with steps={}, stop={}'.format(
            self.steps, self.stop))

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

    @property
    def log_file(self):
        return 'ladder-{}-{}-{}'.format(
            self.api.pair, self.steps, self.stop)

    def run(self):
        logger = getLogger(__name__)

        ticker = self.api.ticker

        if (self.pending_order
                and self.api.order_status(self.pending_order.name) == self.api.CONFIRMED):
            self.api.order_sell(self.pending_order.name, self.api.LIMIT,
                                price=self.pending_order.price + self.stop)

            self.orders.append(self.pending_order)
            self.pending_order = None

        self.orders = [x for x in self.orders if self.api.order_status(x.name) == self.api.PENDING]

        if not self.pending_order and len(self.orders) < self.steps:
            order_name = 'Ladder' + str(len(self.orders))
            price = ticker.last - self.stop
            volume = self.api.balance[0] / self.steps

            self.api.order_buy(order_name, self.api.LIMIT, volume=volume, price=price)
            self.pending_order = LadderOrder(order_name, price, len(self.orders))

            logger.debug('placed limit buy order {}'.format(self.pending_order))

        logger.info('last={:.5f}, pending={}, orders={}'.format(
            ticker.last, self.pending_order, self.orders))

    def clean_up(self):
        pass
