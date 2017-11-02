import logging

from .indicator import mom
from .strategy import Strategy



class MomentumStrategy(Strategy):
    def __init__(self, api, length, *args, **kwargs):
        super().__init__(api, *args, **kwargs)

        self.length = length

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
        logger = logging.getLogger(__name__)

        mom0 = mom(self.api.close(limit=self.length), self.length)
        mom1 = mom(mom0, 1)

        logger.debug(mom0)
        logger.debug(mom1)

    def clean_up(self):
        pass
