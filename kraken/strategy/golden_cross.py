import kraken
from kraken.strategy import KrakenStrategy
from kraken.indicator import sma


class GoldenCross(KrakenStrategy):
    def parse_config(self, config):
        self.fast_sma = int(config['fast_sma'])
        self.slow_sma = int(config['slow_sma'])

    def run(self):
        k = kraken.KrakenAPI()

        ohlc = k.get_ohlc(self.pair, self.interval)
        close = [x.close for x in ohlc]

        fast_sma = sma(close, self.fast_sma)
        slow_sma = sma(close, self.slow_sma)

        return KrakenStrategy.LONG if fast_sma > slow_sma else KrakenStrategy.SHORT
