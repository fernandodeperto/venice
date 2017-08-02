import sys

from os.path import expanduser
from configparser import ConfigParser
from abc import ABCMeta, abstractmethod

class KrakenStrategy(metaclass=ABCMeta):
    SHORT, NEUTRAL, LONG = (-1, 0, 1)

    def __init__(self, pair, interval):
        self.pair = pair
        self.interval = interval

        self.parse_config(self.get_config())

    def get_config(self):
        config = ConfigParser()
        config.read(expanduser('~') + '/.krakenst.conf')


        module_name = self.__module__.split('.')[-1]
        return config[module_name]

    @abstractmethod
    def parse_config(self, config):
        pass

    @abstractmethod
    def run(self):
        pass
