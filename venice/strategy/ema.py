from decimal import Decimal
from logging import getLogger

from .strategy import Strategy
from .indicator import ema


class EMAStrategy(Strategy):
    def __init__(self, api, fast_ema, slow_ema, *args, **kwargs):
        super().__init__(api, *args, **kwargs)

        self.fast_ema = fast_ema
        self.slow_ema = slow_ema

        self.current = None
        self.pending = None

    @staticmethod
    def descr_text():
        return 'Simple EMA crossing strategy'

    @staticmethod
    def help_text():
        return 'EMA crossing strategy'

    @staticmethod
    def configure_parser(parser):
        parser.add_argument('fast_ema', type=int, help='Fast EMA period')
        parser.add_argument('slow_ema', type=int, help='Slow EMA period')

    def run(self):
        logger = getLogger(__name__)

        close = [x.close for x in self.api.ohlc(limit=100)]
        ema_fast = ema(close, self.fast_ema)
        ema_slow = ema(close, self.slow_ema)

        logger.debug('close={}, ema_fast={}, ema_slow={}'.format(
            close[-1], ema_fast[-1], ema_slow[-1]))

        if self.pending:
            order_status = self.api.order_status('EMA')

            # Buy order
            if order_status == self.api.CONFIRMED:
                if self.pending.direction == self.api.BUY:
                    self.current = self.pending
                    self.pending = None

                else:
                    self.current = None
                    self.pending = None

        if ema_fast[-1] > ema_slow[-1]:
            if not self.current and not self.pending:
                self.pending = self.api.order_buy('EMA', self.api.MARKET)

        else:
            if self.current and not self.pending:
                self.pending = self.api.order_sell('EMA', self.api.MARKET)

        logger.debug('current={}, pending={}'.format(self.current, self.pending))

    def clean_up(self):
        pass
