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

        if self.pending:
            order_status = self.api.order_status('Momentum')

            if order_status == self.api.OPEN:
                logger.debug('buy order {} confirmed'.format(self.pending))

                self.current = self.pending
                self.pending = None

            elif order_status == self.api.CLOSED:
                logger.debug('sell order {} confirmed'.format(self.pending))

                self.current = None
                self.pending = None

        if not self.current and mom0[-1] > EPSILON and mom1[-1] > EPSILON:
            if self.pending:
                self.api.cancel('Momentum')

            self.pending = self.api.order_buy('Momentum', self.api.STOP, price=high[-1])
            logger.info('stop buy @ {:.5f}'.format(ticker.last))

        elif self.current and mom0[-1] < -EPSILON and mom1[-1] < -EPSILON:
            if self.pending:
                self.api.cancel('Momentum')

            self.pending = self.api.order_sell('Momentum', self.api.STOP, price=low[-1])
            logger.info('stop sell @ {:.5f}'.format(ticker.last))

        elif self.pending:
            self.api.cancel('Momentum')
            self.pending = None

        logger.debug('last={:.5f}, mom0={:.5f}, mom1={:.5f}, current={}, pending={}'.format(
            ticker.last, mom0[-1], mom1[-1], self.current, self.pending))

    def clean_up(self):
        pass
