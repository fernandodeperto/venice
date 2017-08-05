import logging

from kraken.strategy import KrakenStrategy, KrakenStrategyAPI
from kraken.indicator import mom


class Momentum(KrakenStrategy):
    def parse_config(self, config):
        self.length = int(config['length'])

    def run(self):
        logger = logging.getLogger(__name__)

        ohlc = self.k.get_ohlc(self.pair, self.interval)
        close = [x.close for x in ohlc]

        momentum = mom(close, self.length)

        logger.debug('Momentum: %.3f', momentum[-1])

        k = KrakenStrategyAPI()

        if momentum[-1] >= 0:
            k.cancel_entry('MomES')
            k.add_entry('MomEL', 'buy', 'stop-loss', price=ohlc[-1].high)
        else:
            k.cancel_entry('MomEL')
            k.add_entry('MomES', 'sell', 'stop-loss', price=ohlc[-1].low)
