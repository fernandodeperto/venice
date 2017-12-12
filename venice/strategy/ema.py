from logging import getLogger

from .strategy import Strategy
from .indicator import ema


class EMAStrategy(Strategy):
    def __init__(self, api, fast_ema, slow_ema, cross, *args, **kwargs):
        logger = getLogger(__name__)

        super().__init__(api, *args, **kwargs)

        self.fast_ema = fast_ema
        self.slow_ema = slow_ema
        self.previous_ema = None

        self.current = None
        self.pending = None

        self.cross = cross

        logger.debug(
            'ema strategy started with fast_ema={}, slow_ema={}, cross={}'.format(
                self.fast_ema, self.slow_ema, self.cross))

    @staticmethod
    def descr_text():
        return 'Simple EMA crossing strategy'

    @staticmethod
    def help_text():
        return 'EMA crossing strategy'

    @staticmethod
    def configure_parser(parser):
        parser.add_argument('-c', '--cross', action="store_true", help="enable EMA cross")
        parser.add_argument('fast_ema', type=int, help='Fast EMA period')
        parser.add_argument('slow_ema', type=int, help='Slow EMA period')

    def run(self):
        logger = getLogger(__name__)

        close = [x.close for x in self.api.ohlc(limit=100)]

        ema_fast = ema(close, self.fast_ema)[-1]
        ema_slow = ema(close, self.slow_ema)[-1]

        logger.debug('close={}, ema_fast={}, ema_slow={}, previous_ema={}'.format(
            close[-1], ema_fast, ema_slow, self.previous_ema))

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

        if ema_fast >= ema_slow and (not self.cross or (self.previous_ema and
                                                        self.previous_ema < ema_slow)):
            if not self.current and not self.pending:
                self.pending = self.api.order_buy('EMA', self.api.MARKET)

        else:
            if self.current and not self.pending:
                self.pending = self.api.order_sell('EMA', self.api.MARKET)

        if self.cross:
            self.previous_ema = ema_fast

        logger.debug('current={}, pending={}'.format(self.current, self.pending))

    def clean_up(self):
        pass
