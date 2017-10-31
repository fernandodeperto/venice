import logging

from .strategy import Strategy


class LadderStrategy(Strategy):
    def __init__(self, api, *args, **kwargs):
        super().__init__(api, *args, **kwargs)

    @staticmethod
    def descr_text():
        return 'Ladder strategy'

    @staticmethod
    def help_text():
        return 'Ladder strategy'

    @staticmethod
    def configure_parser(parser):
        pass

    def run(self):
        return None

    def clean_up(self):
        pass
