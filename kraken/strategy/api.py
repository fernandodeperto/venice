import sys

from kraken.api import *


class KrakenStrategyAPI(KrakenAPI):
    _MIN_REFRESH_TIME = 15

    _ohlc = {}

    def get_ohlc(self, pair, interval, since=None):
        key = '-'.join([pair, interval])
        time = KrakenAPI.get_server_time()

        if (key in KrakenStrategyAPI._ohlc and
                KrakenStrategyAPI._ohlc[key][-1].time < time + self._MIN_REFRESH_TIME):
            return KrakenStrategyAPI._ohlc[key]

        # Just update the last candle and return
        if key in KrakenStrategyAPI._ohlc:
            time_next = KrakenStrategyAPI._ohlc[key][-2].time + interval

            if time < time_next:
                KrakenStrategyAPI._ohlc[key][-1] = KrakenAPI.get_ohlc(pair, interval, since=time)
            else:
                ohlc = KrakenAPI.get_ohlc(pair, interval, since=time_next)

                KrakenStrategyAPI._ohlc[key][-1] = ohlc[0]
                KrakenStrategyAPI._ohlc[key].append(ohlc[1])

        else:
            KrakenStrategyAPI._ohlc[key] = KrakenAPI.get_ohlc(pair, interval)

        return KrakenStrategyAPI._ohlc[key]
