import logging

from .strategy import Strategy

class ExampleStrategy(Strategy):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def help_text():
        return 'Example strategy'

    def configure_parser(parser):
        pass

    def run(self):
        logger = logging.getLogger(__name__)
        logger.debug('Running example strategy')
