import importlib
import inspect
import signal
import time
import collections
import argparse
# import sys
import logging
import logging.config

import argcomplete

from kraken.strategy import KrakenStrategy, KrakenStrategyAPI

KrakenStrategyModule = collections.namedtuple(
    'KrakenStrategyModule',
    'module_name class_name value')


def main():
    def signal_handler(sig, frame):
        nonlocal run
        run = 0

    parser = argparse.ArgumentParser(description='bot based on a strategy')
    parser.add_argument('pair', help='asset pair')
    parser.add_argument('-l', '--live', action='store_true', help="enable trade mode")
    parser.add_argument('volume', type=float, help='main currency volume')
    parser.add_argument('volume2', type=float, help='quote currency volume')
    parser.add_argument('interval', help='candle interval')
    parser.add_argument('refresh', type=int, help='time between updates')
    parser.add_argument('strategy', help='trading strategy')

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    logging.config.fileConfig('logging.conf')
    # logger = logging.getLogger()

    run = 1
    signal.signal(signal.SIGINT, signal_handler)

    interval = parse_interval(args.interval)

    if not interval:
        raise ValueError('invalid interval', args.interval)

    strategy = load_module(args.strategy).value()

    api = KrakenStrategyAPI(args.pair, args.volume, args.volume2, args.interval)

    while run:
        start_time = time.time()

        api.update_order()

        strategy.run()

        sleep_time = args.refresh - (time.time() - start_time)
        if sleep_time > 0:
            time.sleep(sleep_time)


def load_module(module_name):
    parent_modules = __name__.split('.')
    module_name = '.'.join(parent_modules[0:len(parent_modules) - 1] +
                           ['strategy', module_name])

    module = importlib.import_module(module_name)

    classes = []
    for name, value in inspect.getmembers(module, inspect.isclass):
        if issubclass(value, KrakenStrategy) and value != KrakenStrategy:
            classes.append(KrakenStrategyModule(module_name, name, value))

    if len(classes) > 1:
        raise ValueError('module {} has more than one valid class'.format(module_name))

    return classes[0]


def parse_interval(interval):
    keys = {
        '1': 1, '5': 5, '15': 15, '30': 30, '60': 60, '240': 240,
        '1H': 60, '4H': 240}

    if interval in keys:
        return keys[interval]
