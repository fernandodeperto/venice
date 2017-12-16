from logging import getLogger

from .indicator import mom
from .strategy import Strategy
from venice.util import EPSILON


class MomentumStrategy(Strategy):
    def __init__(self, api, length, *args, **kwargs):
        logger = getLogger(__name__)

        super().__init__(api, *args, **kwargs)

        self.length = length

        self.current = None
        self.pending = None

        logger.debug('momentum strategy started with length={}'.format(self.length))

    @staticmethod
    def descr_text():
        return 'Momentum strategy'

    @staticmethod
    def help_text():
        return 'Momentum strategy'

    @staticmethod
    def configure_parser(parser):
        parser.add_argument('length', type=int, help='Momentum length')

    @property
    def log_file(self):
        return 'momentum-{}-{}'.format(
            self.api.pair, self.length)

    def run(self):
        logger = getLogger(__name__)

        ohlc = self.api.ohlc(limit=self.length + 1)
        close = [x.close for x in ohlc]
        high = [x.high for x in ohlc]
        low = [x.low for x in ohlc]

        mom0 = mom(close, self.length)
        mom1 = mom(mom0, 1)

        logger.debug('last={:.5f}, mom0={:.5f}, mom1={:.5f}'.format(
            close[-1], mom0[-1], mom1[-1]))

        if self.pending:
            order_status = self.api.order_status('Momentum')

            if order_status == self.api.CONFIRMED:
                if self.pending.direction == self.api.BUY:
                    self.current = self.pending
                    self.pending = None

                else:
                    self.current = None
                    self.pending = None

            elif order_status == self.api.CANCELED:
                del self.pending

        if mom0[-1] > EPSILON and mom1[-1] > EPSILON:
            if self.pending and self.pending.direction == self.api.SELL:
                    self.api.cancel('Momentum')

            elif not self.current and not self.pending:
                self.pending = self.api.order_buy('Momentum', self.api.STOP, price=high[-1])

        elif mom0[-1] < -EPSILON and mom1[-1] < -EPSILON:
            if self.pending and self.pending.direction == self.api.BUY:
                    self.api.cancel('Momentum')

            elif self.current and not self.pending:
                self.pending = self.api.order_sell('Momentum', self.api.STOP, price=low[-1])

        elif self.pending:
            self.api.cancel('Momentum')
            self.pending = None

        logger.debug('current={}, pending={}'.format(
            self.current, self.pending))

    def clean_up(self):
        pass
