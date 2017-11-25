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
        ohlc = self.api.ohlc(limit=self.length)

        close = [x.close for x in ohlc]
        high = [x.high for x in ohlc]
        low = [x.low for x in ohlc]

        mom0 = mom(close, self.length)
        mom1 = mom(mom0, 1)

        logger.info('last={:.5f}, mom0={:.5f}, mom1={:.5f}'.format(
            ticker.last, mom0[-1], mom1[-1]))

        if self.pending:
            order_status = self.api.order_status('Momentum')

            if order_status == self.api.OPEN:
                self.current = self.pending
                self.pending = None

            elif order_status == self.api.CLOSED:
                self.current = None
                self.pending = None

        if mom0[-1] > EPSILON and mom1[-1] > EPSILON and not self.current:
            if self.pending:
                self.api.cancel('Momentum')

            self.pending = self.api.order_buy('Momentum', self.api.STOP, price=high[-1])
            logger.info('stop buy @ {:.5f}'.format(self.pending))

        elif mom0[-1] < -EPSILON and mom1[-1] < -EPSILON and self.current:
            if self.pending:
                self.api.cancel('Momentum')

            self.pending = self.api.order_sell('Momentum', self.api.STOP, price=low[-1])
            logger.info('stop sell @ {:.5f}'.format(self.pending))

        elif self.pending:
            self.api.cancel('Momentum')
            self.pending = None

    def clean_up(self):
        pass
