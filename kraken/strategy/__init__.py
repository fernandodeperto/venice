import sys
import os.path
import configparser
import abc

from kraken.strategy.api import KrakenStrategyAPI

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
