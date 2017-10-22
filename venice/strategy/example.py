import logging

from .strategy import Strategy
from .indicator import crossover, crossunder, sma


class ExampleStrategy(Strategy):
    def __init__(self, api, **kwargs):
        super().__init__(api, **kwargs)

        self.go = 1

    @staticmethod
    def descr_text():
        return 'Example strategy used to test the strategy API'

    @staticmethod
    def help_text():
        return 'Example strategy'

    def configure_parser(parser):
        pass

    def run(self):
        logger = logging.getLogger(__name__)

        if self.go == 1:
            self.api.order_buy('TestOrder', 0.1, stop=69)
            self.go = 0

        return None
