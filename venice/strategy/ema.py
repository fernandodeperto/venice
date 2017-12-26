from decimal import Decimal
from logging import getLogger
from time import time

from .strategy import Strategy
from .indicator import ema
from ..util import EPSILON


class EMAStrategy(Strategy):
    def __init__(self, api, fast_ema, slow_ema, cross, epsilon, *args, **kwargs):
        logger = getLogger(__name__)

        super().__init__(api, *args, **kwargs)

        self.fast_ema = fast_ema
        self.slow_ema = slow_ema

        self.cross = cross
        self.first_cross = False

        self.epsilon = Decimal.from_float(epsilon) if epsilon else EPSILON

        self.current = None
        self.pending = None

        logger.debug('ema strategy started with fast_ema={:.5f}, slow_ema={:.5f}, cross={}, '
                     'epsilon={:.5f}'.format(
                         self.fast_ema, self.slow_ema, self.cross, self.epsilon))

    @staticmethod
    def descr_text():
        return 'Simple EMA crossing strategy'

    @staticmethod
    def help_text():
        return 'EMA crossing strategy'

    @staticmethod
    def configure_parser(parser):
        parser.add_argument('-c', '--cross', action='store_true', help='enable EMA cross')
        parser.add_argument('-e', '--epsilon', type=float, help='use a specific epsilon')
        parser.add_argument('fast_ema', type=int, help='Fast EMA period')
        parser.add_argument('slow_ema', type=int, help='Slow EMA period')

    @property
    def log_file(self):
        return 'ema-{}-{}-{}-{}'.format(self.api.pair, self.fast_ema, self.slow_ema, self.cross)

    def run(self):
        logger = getLogger(__name__)

        close = self.api.close(limit=100)
        high = self.api.high(limit=100)
        low = self.api.low(limit=100)

        ema_fast = ema(close, self.fast_ema)
        ema_slow = ema(close, self.slow_ema)

        if self.cross and not self.first_cross and ema_fast[-1] < ema_slow[-1]:
            self.first_cross = True

        logger.debug('close={:.5f}, ema_fast={:.5f}, ema_slow={:.5f}, first_cross={}'.format(
            close[-1], ema_fast[-1], ema_slow[-1], self.first_cross))

        if self.pending:
            self.pending = self.api.order_status('EMA', self.pending.direction)

            # Buy order
            if self.pending == self.api.CONFIRMED:
                if self.pending.direction == self.api.BUY:
                    self.current = self.pending
                    self.pending = None

                else:
                    self.current = None
                    self.pending = None

        if ema_fast[-1] - ema_slow[-1] > self.epsilon and not self.current and not self.pending:
            if self.cross and not self.first_cross:
                logger.debug('EMA is higher but first cross has not been achieved')

            else:
                self.pending = self.api.order_buy('EMA', self.api.STOP, price=high[-1])

        elif ema_fast[-1] - ema_slow[-1] < -self.epsilon:
                if not self.current and self.pending:
                    self.api.cancel()

                elif self.current and not self.pending:
                    self.pending = self.api.order_sell('EMA', self.api.STOP, price=low[-1])

        logger.debug('current={}, pending={}'.format(self.current, self.pending))

    def clean_up(self):
        pass
