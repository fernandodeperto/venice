from logging import getLogger

from .strategy import Strategy
from .indicator import sma


class SMAStrategy(Strategy):
    def __init__(self, api, fast_sma, slow_sma, *args, **kwargs):
        logger = getLogger(__name__)

        super().__init__(api, *args, **kwargs)

        self.fast_sma = fast_sma
        self.slow_sma = slow_sma

        self.current = None
        self.pending = None

        logger.debug('sma strategy started with fast_sma={}, slow_sma={}'.format(
            self.fast_sma, self.slow_sma))

    @staticmethod
    def descr_text():
        return 'Simple SMA crossing strategy'

    @staticmethod
    def help_text():
        return 'SMA crossing strategy'

    @staticmethod
    def configure_parser(parser):
        parser.add_argument('fast_sma', type=int, help='Fast SMA period')
        parser.add_argument('slow_sma', type=int, help='Slow SMA period')

    def run(self):
        logger = getLogger(__name__)

        close = [x.close for x in self.api.ohlc(limit=80)]
        sma_fast = sma(close, self.fast_sma)
        sma_slow = sma(close, self.slow_sma)

        logger.debug('close={}, sma_fast={}, sma_slow={}'.format(
            close[-1], sma_fast[-1], sma_slow[-1]))

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

        if sma_fast[-1] > sma_slow[-1]:
            if not self.current and not self.pending:
                self.pending = self.api.order_buy('SMA', self.api.MARKET)

        else:
            if self.current and not self.pending:
                self.pending = self.api.order_sell('SMA', self.api.MARKET)

        logger.debug('current={}, pending={}'.format(self.current, self.pending))

    def clean_up(self):
        pass
