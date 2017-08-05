import logging

from kraken.strategy import mom

from . import KrakenStrategy


class Momentum(KrakenStrategy):
    def parse_config(self, config):
        self.length = int(config['length'])

    def run(self):
        logger = logging.getLogger('momentum')

        ohlc = self.k.get_ohlc(self.pair, self.interval)
        close = [x.close for x in ohlc]

        momentum = mom(close, self.length)

        logger.debug('momentum: %.3f', momentum[-1])
