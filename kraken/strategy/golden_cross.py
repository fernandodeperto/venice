from kraken.strategy import KrakenStrategy
from kraken.indicator import sma
from kraken.strategy.api import KrakenStrategyAPI


class GoldenCross(KrakenStrategy):
    def parse_config(self, config):
        self.fast_sma = int(config['fast_sma'])
        self.slow_sma = int(config['slow_sma'])

    def run(self):
        k = KrakenStrategyAPI()

        ohlc = k.get_ohlc(self.pair, self.interval)
        close = [x.close for x in ohlc]

        fast_sma = sma(close, self.fast_sma)
        slow_sma = sma(close, self.slow_sma)

        print('sma: {:.2f} {:.2f}'.format(fast_sma[-1], slow_sma[-1]))

        return KrakenStrategy.LONG if fast_sma[1] > slow_sma[-1] else KrakenStrategy.SHORT
