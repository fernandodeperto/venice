import os.path
import configparser
import abc
import logging

from kraken.api import KrakenAPI


class KrakenStrategyAPI(KrakenAPI):
    def __init__(self, live=False):
        super().__init__()

        self.live = live
        self.ohlc = {}

    def get_ohlc(self, pair, interval, since=None):
        logger = logging.getLogger(__name__)

        key = '-'.join([pair, str(interval)])

        time = self.get_server_time()

        if key in self.ohlc:
            time_next = self.ohlc[key][-1].time + interval * 60
            # Just update the last candle
            if time < time_next:
                logger.debug('just update, next in %d', time_next - time)

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

    def update_entries(self):
        pass

    def add_entry(self, name, direction, order_type, price=0, price2=0):
        logger = logging.getLogger(__name__)
        logger.info('New entry %s: %s %s @ %.3f %.3f', name, direction, order_type, price, price2)

    def cancel_entry(self, name):
        logger = logging.getLogger(__name__)
        logger.info('Cancel entry %s', name)


class KrakenStrategy(metaclass=abc.ABCMeta):
    def __init__(self, pair, interval, live=False):
        self.pair = pair
        self.interval = interval
        self.live = live

        self.k = KrakenStrategyAPI()

        self.parse_config(self.get_config())

    def get_config(self):
        config = configparser.ConfigParser()
        config.read(os.path.expanduser('~') + '/.krakenst.conf')

        module_name = self.__module__.split('.')[-1]
        return config[module_name]

    @abc.abstractmethod
    def parse_config(self, config):
        pass

    @abc.abstractmethod
    def run(self):
        pass
