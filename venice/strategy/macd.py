from decimal import Decimal
from logging import getLogger
from time import time

from .strategy import Strategy
from .indicator import ema, macd
from ..util import EPSILON


class MACDStrategy(Strategy):
    def __init__(self, api, fast_length, slow_length, signal_length, cross, epsilon, *args,
                 **kwargs):
        logger = getLogger(__name__)

        super().__init__(api, *args, **kwargs)

        self.fast_length = fast_length
        self.slow_length = slow_length
        self.signal_length = signal_length

        self.cross = cross
        self.first_cross = False

        self.epsilon = Decimal.from_float(epsilon) if epsilon else EPSILON

        self.current = None
        self.pending = None

        logger.debug('macd strategy started with fast_length={}, slow_length={}, '
                     'signal_length={}, cross={}, epsilon={}'.format(
                         self.fast_length, self.slow_length, self.signal_length, self.cross,
                         self.epsilon))

    @staticmethod
    def descr_text():
        return 'Simple MACD crossing strategy'

    @staticmethod
    def help_text():
        return 'MACD crossing strategy'

    @staticmethod
    def configure_parser(parser):
        parser.add_argument('-c', '--cross', action='store_true', help='require MACD cross')
        parser.add_argument('-e', '--epsilon', type=float, help='use a specific epsilon')
        parser.add_argument('fast_length', type=int, help='Fast MACD length')
        parser.add_argument('slow_length', type=int, help='Slow MACD length')
        parser.add_argument('signal_length', type=int, help='MACD signal length')

    @property
    def log_file(self):
        return 'macd-{}-{}-{}-{}'.format(
            self.api.pair, self.cross, self.epsilon, self.fast_length, self.slow_length,
            self.signal_length)

    def run(self):
        logger = getLogger(__name__)

        close = self.api.close(limit=100)
        high = self.api.high(limit=100)
        low = self.api.low(limit=100)

        macd_, signal, histogram = macd(
            self.fast_length, self.slow_length, close, self.signal_length)

        if self.cross and not self.first_cross and macd_[-1] < signal[-1]:
            self.first_cross = True

        logger.debug('close={:.5f}, macd={:.5f}, signal={:.5f}, histogram={}, '
                     'first_cross={}'.format(
                         close[-1], macd_[-1], signal[-1], histogram[-1], self.first_cross))

        if self.pending:
            self.pending = self.api.order_status('MACD', self.pending.direction)

            if self.pending.status == self.api.CONFIRMED:
                if not self.current:
                    self.current = self.pending
                    self.pending = None

                else:
                    self.current = None
                    self.pending = None

            elif self.pending.status == self.api.CANCELED:
                self.pending = None

        if macd_[-1] - signal[-1] > self.epsilon and not self.current and not self.pending:
            if self.cross and not self.first_cross:
                logger.debug('MACD is higher but first cross has not been achieved')

            else:
                self.pending = self.api.order_buy('MACD', self.api.STOP, price=high[-1])

        elif macd_[-1] - signal[-1] < -self.epsilon:
                # Buy order pending
                if self.pending and not self.current:
                    self.api.cancel()

                elif self.current and not self.pending:
                    self.pending = self.api.order_sell('MACD', self.api.STOP, price=low[-1])

        logger.debug('current={}, pending={}'.format(self.current, self.pending))

    def clean_up(self):
        pass
