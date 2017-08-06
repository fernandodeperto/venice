import sys
import os.path
import configparser
import abc
import logging

from collections import namedtuple

from kraken.api import KrakenAPI

KrakenStrategyEntry = namedtuple(
    'KrakenStrategyEntry',
    'direction order_type price price2 txid')


class KrakenStrategyAPI(KrakenAPI):
    pending_entries = {}
    confirmed_entries = {}

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

        entry = KrakenStrategyEntry(direction, order_type, price, price2, None)

        if name in self.__class__.pending_entries:
            logger.info('Update entry %s: %s %s @ %.3f %.3f', name, direction, order_type,
                        price, price2)
            self._update_entry(name, entry)

        elif name in self.__class__.confirmed_entries:
            logger.info('Entry %s already confirmed', name)

        else:
            logger.info('New entry %s: %s %s @ %.3f %.3f', name, direction, order_type, price,
                        price2)
            self._add_entry(name, entry)

    def cancel_entry(self, name):
        logger = logging.getLogger(__name__)

        if name in self.__class__.pending_entries:
            logger.info('Cancel pending entry %s', name)

        elif name in self.__class__.confirmed_entries:
            logger.info('Cancel confirmed entry %s', name)

        else:
            logger.info('Entry %s not found', name)

    def _update_entry(self, name, entry):
        pass

    def _add_entry(self, name, entry):
        pass


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
