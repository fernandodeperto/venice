"""
Golden cross strategy.
"""
from kraken.strategy import KrakenStrategy


class GoldenCross(KrakenStrategy):
    """
    Golden cross main class.
    """
    def parse_config(self, config):
        self.fast_sma = config['fast_sma']
        self.slow_sma = config['slow_sma']
