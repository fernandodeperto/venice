import logging

from kraken.api import KrakenAPI


class KrakenStrategyAPI(KrakenAPI):
    def __init__(self, live=False):
        super().__init__()

        self.live = live
        self.ohlc = {}

    def get_ohlc(self, pair, interval, since=None):
        logger = logging.getLogger('strategy_api')

        key = '-'.join([pair, str(interval)])

        time = self.get_server_time()
        logger.debug('current time: %s', time)

        if key in self.ohlc:
            time_next = self.ohlc[key][-1].time + interval * 60
            logger.debug('next time: %s', time_next)

            # Just update the last candle
            if time < time_next:
                logger.debug('just update')

                ohlc = super().get_ohlc(pair, interval, since=time)
                self.ohlc[key][-1] = ohlc[0]

            # Update the previous candle and add the new one
            else:
                logger.debug('update previous and add')

                ohlc = super().get_ohlc(pair, interval, since=time_next)

                self.ohlc[key][-1] = ohlc[0]
                self.ohlc[key].append(ohlc[1])

        # Get new data
        else:
            logger.debug('get new data')

            self.ohlc[key] = super().get_ohlc(pair, interval)

        return self.ohlc[key]
