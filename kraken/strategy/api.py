from kraken.api import KrakenAPI


class KrakenStrategyAPI(KrakenAPI):
    def __init__(self, live=False):
        super().__init__()

        self.live = live
        self.ohlc = {}

    def get_ohlc(self, pair, interval, since=None):
        key = '-'.join([pair, str(interval)])
        time = self.get_server_time()

        if key in self.ohlc:
            time_next = self.ohlc[key][-1].time + interval * 60

            # Just update the last candle
            if time < time_next:
                ohlc = super().get_ohlc(pair, interval, since=time)
                self.ohlc[key][-1] = ohlc[0]

            # Update the previous candle and add the new one
            else:
                ohlc = super().get_ohlc(pair, interval, since=time_next)

                self.ohlc[key][-1] = ohlc[0]
                self.ohlc[key].append(ohlc[1])

        # Get new data
        else:
            self.ohlc[key] = super().get_ohlc(pair, interval)

        return self.ohlc[key]
