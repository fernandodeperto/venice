import logging

from .strategy import Strategy

class MomentumStrategy(Strategy):
    def __init__(self, api, *args, **kwargs):
        super().__init__(api, *args, **kwargs)

        @staticmethod
        def descr_text():
            return 'Momentum strategy'

        @staticmethod
        def help_text():
            return 'Momentum strategy'

        @staticmethod
        def configure_parser():
            pass

        def run(self):
            return None

        def clean_up(self):
            pass
