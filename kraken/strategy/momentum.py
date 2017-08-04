from kraken.strategy import KrakenStrategy
from kraken.indicator import mom


class Momentum(KrakenStrategy):
    def parse_config(self, config):
        self.length = int(config['length'])

    def run(self):
        ohlc = self.k.get_ohlc(self.pair, self.interval)
        close = [x.close for x in ohlc]

        momentum = mom(close, self.length)
