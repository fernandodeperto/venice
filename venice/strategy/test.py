from logging import getLogger

from .strategy import Strategy


class TestStrategy(Strategy):
    def __init__(self, api, *args, **kwargs):
        logger = getLogger(__name__)

        super().__init__(api, *args, **kwargs)

        self.current = None
        self.pending = None

        logger.debug('test strategy started')

    @staticmethod
    def descr_text():
        return 'Test strategy'

    @staticmethod
    def help_text():
        return 'Test strategy'

    @staticmethod
    def configure_parser(parser):
        pass

    @property
    def log_file(self):
        return 'test-{}'.format(self.api.pair)

    def run(self):
        logger = getLogger(__name__)

        ticker = self.api.ticker

        logger.debug('last={:.5f}'.format(ticker.last))

        if self.pending:
            order_status = self.api.order_status('Test')

            # Buy order
            if order_status == self.api.CONFIRMED:
                if self.pending.direction == self.api.BUY:
                    self.current = self.pending
                    self.pending = None

                else:
                    self.current = None
                    self.pending = None

        if not self.pending and not self.current:
            self.pending = self.api.order_buy('Test', self.api.MARKET)

        elif not self.pending and self.current:
            self.pending = self.api.order_sell('Test', self.api.MARKET)

        logger.debug('current={}, pending={}'.format(
            self.current, self.pending))

    def clean_up(self):
        pass
