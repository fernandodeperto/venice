from decimal import Decimal
from logging import getLogger

from .strategy import Strategy


class TrailingStrategy(Strategy):
    def __init__(self, api, stop, *args, **kwargs):
        logger = getLogger(__name__)

        super().__init__(api, *args, **kwargs)

        self.stop = Decimal.from_float(stop)
        self.buy_order = None

        logger.info('trailing stop started with stop={}'.format(self.stop))

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
        logger = getLogger(__name__)

        ticker = self.api.ticker()

        if not self.buy_order:
            self.order = self.api.order_buy('Trailing0', self.api.TRAILING_STOP, price=self.stop)

        else:
            order_status = self.api.order_status('Trailing0')

            if order_status == self.api.OPEN:
                self.order = self.api.order_sell('Trailing0', self.api.TRAILING_STOP,
                                                 price=self.stop)

            elif order_status == self.api.CLOSED:
                self.order = None

        logger.info('last={:.5f}, order={}'.format(ticker.last, self.order))

    def clean_up(self):
        pass
