from logging import getLogger

from .indicator import mom
from .strategy import Strategy
from venice.util import EPSILON


class MomentumStrategy(Strategy):
    def __init__(self, api, length, *args, **kwargs):
        super().__init__(api, *args, **kwargs)

        self.length = length

        self.current = None
        self.pending = None

    @staticmethod
    def descr_text():
        return 'Momentum strategy'

    @staticmethod
    def help_text():
        return 'Momentum strategy'

    @staticmethod
    def configure_parser(parser):
        parser.add_argument('length', type=int, help='Momentum length')

    def run(self):
        logger = getLogger(__name__)

        ticker = self.api.ticker()
        ohlc = self.api.ohlc(limit=self.length + 1)

        close = [x.close for x in ohlc]
        high = [x.high for x in ohlc]
        low = [x.low for x in ohlc]
        mom0 = mom(close, self.length)
        mom1 = mom(mom0, 1)

        if self.pending:
            order_status = self.api.order_status('Momentum')

            # Buy order
            if order_status == self.api.CONFIRMED:
                if self.pending.direction == self.api.BUY:
                    self.current = self.pending
                    self.pending = None

                else:
                    self.current = None
                    self.pending = None

        if mom0[-1] > EPSILON and mom1[-1] > EPSILON:
            if self.pending and self.pending.direction == self.api.SELL:
                    self.api.cancel('Momentum')
                    self.pending = None

            if not self.current and not self.pending:
                self.pending = self.api.order_buy('Momentum', self.api.STOP, price=high[-1])

        elif mom0[-1] < -EPSILON and mom1[-1] < -EPSILON:
            if self.pending and self.pending.direction == self.api.BUY:
                    self.api.cancel('Momentum')
                    self.pending = None

            if self.current and not self.pending:
                self.pending = self.api.order_sell('Momentum', self.api.STOP, price=low[-1])

        elif self.pending:
            self.api.cancel('Momentum')
            self.pending = None

        logger.debug('last={:.5f}, mom0={:.5f}, mom1={:.5f}, current={}, pending={}'.format(
            ticker.last, mom0[-1], mom1[-1], self.current, self.pending))

    def clean_up(self):
        pass
