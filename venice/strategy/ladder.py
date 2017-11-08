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

        logger.info('ladder strategy started with {} steps, stop={:.5f}'.format(
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

    def run(self):
        logger = getLogger(__name__)

        ticker = self.api.ticker()
        self.pivot = max(self.pivot, ticker.last)

        # Place pending sell order
        if self.pending_order:
            try:
                self.api.order_sell(self.pending_order.name,
                                    limit=self.pending_order.price + self.stop)

            except Exception:
                logger.warning('could not place pending buy order {}'.format(self.pending_order))
                raise

            self.pending_order = None

        while self.orders and ticker.last >= self.orders[-1].price + self.stop:
            # Check if order was confirmed. If not, break loop
            try:
                order_status = self.api.order_status(self.orders[-1].name)

            except Exception:
                logger.warning('could not confirm order {}'.format(self.orders[-1]))
                raise

            if order_status.status == self.api.CLOSED:
                logger.info('sell order {} closed @ {}'.format(self.orders[-1], ticker.last))
                order = self.orders.pop()

            else:
                logger.warning('sell order {} not closed'.format(self.orders[-1]))
                break

            logger.info('closed sell order @ {}: {}'.format(ticker.last, order))

        if len(self.orders) < self.steps and ticker.last <= self.pivot - self.stop:
            order_name = 'Ladder' + str(len(self.orders))
            volume = self.api.capital / self.steps / ticker.last

            # Place market buy order. If unsuccessful, return
            try:
                self.api.order_buy(order_name, volume=volume)

            except Exception:
                logger.warning('could not place market order')
                raise

            order = LadderOrder(order_name, ticker.last, self.steps)

            # Place limit sell order. If unsuccessful, save it in the list
            try:
                self.api.order_sell(order_name, limit=ticker.last + self.stop)

            except:
                self.pending_order = order

                logger.warning('could not place limit order {}'.format(order))
                raise

            self.orders.append(order)
            self.pivot = ticker.last

            logger.info('closed buy order {} @ {}'.format(order, ticker.last))

        logger.info('last={:.5f}, pivot={:.5f}, orders={}'.format(
            ticker.last, self.pivot, self.orders))

    def clean_up(self):
        pass
