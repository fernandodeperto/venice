"""
Basic strategy package module.
"""
import importlib
import inspect
import sys
import signal
import time

from os import listdir
from os.path import isfile, join, dirname, splitext, expanduser
from collections import namedtuple
from configparser import ConfigParser
from abc import ABCMeta, abstractmethod
from time import sleep

from argparse import ArgumentParser
from argcomplete import autocomplete

# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods

KrakenStrategyTuple = namedtuple('KrakenStrategyTuple', 'module_name class_name value')

class KrakenStrategy(metaclass=ABCMeta):
    """
    Basic strategy class, supposed to be inherited.
    """
    LONG = 1
    NEUTRAL = 0
    SHORT = -1

    def __init__(self):
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
    def get_position(self, ohlc, ticker):
        pass


def main():
    parser = ArgumentParser(description='run a bot that uses strategies to decide when to enter and close positions')
    parser.add_argument('pair', help='asset pair')
    parser.add_argument('volume', type=float, help='main currency volume')
    parser.add_argument('volume2', type=float, help='quote currency volume')
    parser.add_argument('interval', help='candle interval')
    parser.add_argument('refresh', help='time between updates')
    parser.add_argument('strategy', nargs='+', help='list of strategies')

    autocomplete(parser)
    args = parser.parse_args()

    run = 1

    def signal_handler(signal, frame):
        nonlocal run
        run = 0

    signal.signal(signal.SIGINT, signal_handler)

    classes = load_modules(args.strategy)
    strategies = [x.value() for x in classes]

    #TODO get historic ohlc data

    while run:
        start_time = time.time()

        #TODO confirm pending orders

        #TODO update ohlc and ticker data

        #TODO run all strategies
        #TODO check strategies' answers

        #TODO decide position based on the answers

        sleep(int(args.refresh) - (time.time() - start_time))


def load_modules(module_names):
    classes = []

    for module_name in module_names:
        module = importlib.import_module('.'.join([__name__, module_name]))

        for name, value in inspect.getmembers(module, inspect.isclass):
            if issubclass(value, KrakenStrategy) and value != KrakenStrategy:
                classes.append(KrakenStrategyTuple(module_name, name, value))

    return classes
