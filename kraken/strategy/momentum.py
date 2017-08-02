import kraken
from kraken.strategy import KrakenStrategy
from kraken.indicator import mom


class Momentum(KrakenStrategy):
    def parse_config(self, config):
        self.length = int(config['length'])

    def run(self):
        k = kraken.KrakenAPI()

        ohlc = k.get_ohlc(self.pair, self.interval)
        close = [x.close for x in ohlc]

        momentum = mom(close, self.length)
        momentum2 = mom(momentum, 1)

        if momentum[-1] > 0 and momentum2[-1] > 2:
            return KrakenStrategy.LONG
        elif momentum[-1] < 0 and momentum2[-1] < 0:
            return KrakenStrategy.SHORT

        return KrakenStrategy.NEUTRAL
