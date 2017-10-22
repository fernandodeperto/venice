import logging

from .strategy import Strategy
from .indicator import crossover, crossunder, sma


class SMAStrategy(Strategy):
    def __init__(self, api, fast_sma, slow_sma, *args, **kwargs):
        super().__init__(api, *args, **kwargs)

        self.fast_sma = fast_sma
        self.slow_sma = slow_sma

        self.step = 0

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
        logger = logging.getLogger(__name__)

        ticker = self.api.ticker()
        logger.debug(ticker)

        price = ticker.last
        logger.debug(price)

        available_currency = self.api.capital/price
        logger.debug(available_currency)

        if self.step == 0:
            self.api.order_buy('SMATestorder', volume=0.1, limit=40)

            self.step = 1

        elif self.step == 1:
            self.api.cancel('SMATestorder')

            self.step = 2

        elif self.step == 2:
            pass

        return None

        close = [x.close for x in self.api.ohlc()]
        close.reverse()
        sma_fast = sma(close, 7)
        sma_slow = sma(close, 20)

        logger.debug('close={}, sma_fast={}, sma_slow={}, crossover={}, crossunder={}'.format(
            close[-1], sma_fast[-1], sma_slow[-1], crossover(sma_fast, sma_slow),
            crossunder(sma_fast, sma_slow)))

        if crossover(sma_fast, sma_slow):
            # self.api.order_buy('SMALong')
            logger.debug('order_buy')

        elif crossunder(sma_fast, sma_slow):
            # self.api.order_sell('SMAShort')
            logger.debug('order_sell')
