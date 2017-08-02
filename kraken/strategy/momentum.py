from kraken.strategy import KrakenStrategy
from kraken.indicator import mom

import kraken

class Momentum(KrakenStrategy):
    def parse_config(self, config):
        self.length = config['length']

    def run(self):
        k = kraken.KrakenAPI()
        ohlc = k.get_ohlc(self.pair, self.interval)
        print(ohlc)
        # momentum = mom(
