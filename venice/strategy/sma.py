from logging import getLogger

from .strategy import Strategy
from .indicator import crossover, crossunder, sma


class SMAStrategy(Strategy):
    def __init__(self, api, fast_sma, slow_sma, *args, **kwargs):
        super().__init__(api, *args, **kwargs)

        self.fast_sma = fast_sma
        self.slow_sma = slow_sma

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

        logger.debug(
            'close={}, sma=({}, {}), crossover={}, crossunder={}'.format(
                close[-1], sma_fast[-2] - sma_slow[-2], sma_fast[-1] - sma_slow[-1],
                crossover(sma_fast, sma_slow), crossunder(sma_fast, sma_slow)))

        if crossover(sma_fast, sma_slow):
            self.api.order_buy('SMA', self.api.MARKET)

        elif crossunder(sma_fast, sma_slow):
            self.api.order_sell('SMA', self.api.MARKET)

    def clean_up(self):
        pass
