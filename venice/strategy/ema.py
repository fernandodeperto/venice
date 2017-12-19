from decimal import Decimal
from logging import getLogger
from time import time

from .strategy import Strategy
from .indicator import ema
from ..util import EPSILON


class EMAStrategy(Strategy):
    def __init__(self, api, fast_ema, slow_ema, cross, limit, *args, **kwargs):
        logger = getLogger(__name__)

        super().__init__(api, *args, **kwargs)

        self.fast_ema = fast_ema
        self.slow_ema = slow_ema

        self.cross = cross
        self.first_cross = False

        self.limit = Decimal.from_float(limit)

        self.current = None
        self.pending = None

        logger.debug(
            'ema strategy started with fast_ema={:.5f}, slow_ema={:.5f}, first_cross={:.5f}, '
            'limit={}'.format(self.fast_ema, self.slow_ema, self.cross, self.limit))

    @staticmethod
    def descr_text():
        return 'Simple EMA crossing strategy'

    @staticmethod
    def help_text():
        return 'EMA crossing strategy'

    @staticmethod
    def configure_parser(parser):
        parser.add_argument('-c', '--cross', action='store_true', help='enable EMA cross')
        parser.add_argument('-l', '--limit', type=float, help='limit EMA difference')
        parser.add_argument('fast_ema', type=int, help='Fast EMA period')
        parser.add_argument('slow_ema', type=int, help='Slow EMA period')

    @property
    def log_file(self):
        return 'ema-{}-{}-{}-{}-{}'.format(
            self.api.pair, self.fast_ema, self.slow_ema, self.cross, self.limit)

    def run(self):
        logger = getLogger(__name__)

        close = [x.close for x in self.api.ohlc(limit=100)]

        ema_fast = ema(close, self.fast_ema)
        ema_slow = ema(close, self.slow_ema)

        if self.cross and not self.first_cross and ema_fast[-1] < ema_slow[-1]:
            self.first_cross = True

        logger.debug('close={:.5f}, ema_fast={:.5f}, ema_slow={:.5f}, first_cross={}'.format(
            close[-1], ema_fast[-1], ema_slow[-1], self.first_cross))

        if self.pending:
            order_status = self.api.order_status('EMA')

            # Buy order
            if order_status == self.api.CONFIRMED:
                if self.pending.direction == self.api.BUY:
                    self.current = self.pending
                    self.pending = None

                else:
                    self.current = None
                    self.pending = None

        if (ema_fast[-1] - ema_slow[-1] > (self.limit if self.limit else EPSILON) and
                not self.current and not self.pending):
            if self.cross and not self.first_cross:
                logger.debug('EMA is higher but first cross has not been achieved')

            else:
                self.pending = self.api.order_buy('EMA', self.api.MARKET)
                self.previous_order = time()

        elif (ema_fast[-1] - ema_slow[-1] < (-self.limit if self.limit else -EPSILON) and
              self.current and not self.pending):
            self.pending = self.api.order_sell('EMA', self.api.MARKET)
            self.previous_order = time()

        logger.debug('current={}, pending={}'.format(self.current, self.pending))

    def clean_up(self):
        pass
