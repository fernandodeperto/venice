from kraken.api import *


class KrakenStrategyAPI(KrakenAPI):
    _ohlc = None

    @staticmethod
    def get_ohlc(pair, interval, since=None):
        pass
