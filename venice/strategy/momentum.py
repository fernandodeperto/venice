from logging import getLogger

from .indicator import mom
from .strategy import Strategy
from venice.util import EPSILON


class MomentumStrategy(Strategy):
    def __init__(self, api, length, *args, **kwargs):
        super().__init__(api, *args, **kwargs)

        self.length = length

        self.current = None
        self.buy = None
        self.sell = None

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

        if mom0[-1] > EPSILON and mom1[-1] > EPSILON:
            if not self.current and not self.buy:
                self.buy = high[-1]
                logger.info('stop buy @ {:.5f}'.format(self.buy))

        elif mom0[-1] < -EPSILON and mom1[-1] < -EPSILON:
            if self.current:
                self.sell = low[-1]
                logger.info('stop sell @ {:.5f}'.format(self.sell))

        elif self.buy or self.sell:
            self.buy = None
            self.sell = None
            logger.info('cancel')

        if self.buy and ticker.last - self.buy > EPSILON:
            self.buy = None
            self.current = ticker.last
            logger.info('close buy order @ {:.5f}'.format(self.current))

        elif self.sell and ticker.last - self.sell < -EPSILON:
            self.sell = None
            logger.info('close sell order @ {:.5f} with buy order @ {:.5f}'.format(
                ticker.last, self.current))

            self.current = None

    def clean_up(self):
        pass
