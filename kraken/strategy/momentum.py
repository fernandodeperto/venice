import logging

from kraken.strategy import KrakenStrategy, KrakenStrategyAPI
from kraken.indicator import mom


class Momentum(KrakenStrategy):
    def parse_config(self, config):
        self.length = int(config['length'])

    def run(self):
        logger = logging.getLogger(__name__)

        api = KrakenStrategyAPI.api

        ohlc = api.get_ohlc()
        close = [x.close for x in ohlc]

        momentum = mom(close, self.length)
        momentum2 = mom(momentum, 1)

        logger.debug('momentum: %.3f %.2f', momentum[-1], momentum2[-1])

        if momentum[-1] > 0 and momentum2[-1] > 0:
            api.add_order('buy', 'stop-loss', price=ohlc[-1].high)
        elif momentum[-1] < 0 and momentum2[-1] < 0:
            api.add_order('sell', 'stop-loss', price=ohlc[-1].low)
        else:
            api.cancel_order()
