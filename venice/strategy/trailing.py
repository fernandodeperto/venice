from decimal import Decimal
from logging import getLogger

from .strategy import Strategy


class TrailingStrategy(Strategy):
    def __init__(self, api, stop, *args, **kwargs):
        logger = getLogger(__name__)

        super().__init__(api, *args, **kwargs)

        self.stop = Decimal.from_float(stop)

        self.current = None
        self.pending = None

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

        if self.pending:
            order_status = self.api.order_status('Trailing')

            if order_status == self.api.OPEN:
                self.current = self.pending
                self.pending = None

            elif order_status == self.api.CLOSED:
                self.current = None
                self.pending = None

        if not self.current and not self.pending:
            self.pending = self.api.order_buy('Trailing', self.api.TRAILING_STOP, price=self.stop)

        elif self.current and not self.pending:
            self.pending = self.api.order_sell('Trailing0', self.api.TRAILING_STOP,
                                               price=self.stop)

        logger.info('last={:.5f}, order={}'.format(ticker.last, self.order))

    def clean_up(self):
        pass
