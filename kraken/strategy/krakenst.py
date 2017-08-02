import importlib
import inspect
import sys
import signal

import time

from collections import namedtuple

from argparse import ArgumentParser
from argcomplete import autocomplete

# from kraken.strategy import KrakenStrategy

# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods

from kraken.strategy import KrakenStrategy

KrakenStrategyModule = namedtuple('KrakenStrategyModule', 'module_name class_name value')


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

    strategies = [x.value(args.pair, args.interval) for x in load_modules(args.strategy)]

    #TODO convert interval to the right format

    sys.exit()

    while run:
        start_time = time.time()

        #TODO confirm pending orders

        #TODO update ohlc and ticker data

        #TODO run all strategies
        #TODO check strategies' answers

        #TODO decide position based on the answers

        time.sleep(int(args.refresh) - (time.time() - start_time))


def load_modules(module_names):
    classes = []
    parent_modules = __name__.split('.')

    for module_name in module_names:
        module = importlib.import_module(
            '.'.join(parent_modules[0:len(parent_modules) - 1] + [module_name]))

        for name, value in inspect.getmembers(module, inspect.isclass):
            if issubclass(value, KrakenStrategy) and value != KrakenStrategy:
                classes.append(KrakenStrategyModule(module_name, name, value))

    return classes
