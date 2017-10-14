import argparse
import collections
# import importlib
import inspect
import logging
import logging.config
import signal
import sys
import time

import argcomplete

from . import api
from . import strategy

StrategyModule = collections.namedtuple(
    'StrategyModule',
    'module_name class_name value')


def main():
    def signal_handler(sig, frame):
        nonlocal run

        logger = logging.getLogger(__name__)
        logger.info("Signal {} received".format(sig))

        run = 0

    parser = argparse.ArgumentParser(description='bot based on a strategy')
    parser.add_argument('-l', '--live', action='store_true', help="enable trade mode")
    parser.add_argument('exchange', help='exchange to be used')
    parser.add_argument('pair', choices=['btcusd', 'ltcusd', 'ethusd'], help='asset pair')
    parser.add_argument('volume', type=float, help='main currency volume')
    parser.add_argument('period', help='candle period')
    parser.add_argument('refresh', type=int, help='time between updates')

    # Configure the strategies' subparsers
    strategy_parsers = parser.add_subparsers(dest='strategy', title='strategies')
    strategy_parsers.required = True

    strategy_classes = get_classes(strategy, strategy.Strategy)
    configure_parsers(strategy_parsers, strategy_classes)

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    logging.config.fileConfig('logging.conf')
    # logger = logging.getLogger(__name__)

    # Basic initialization
    run = 1
    signal.signal(signal.SIGINT, signal_handler)

    # Initialize the API
    exchange_classes = get_classes(api, api.ExchangeAPI)

    if args.exchange not in exchange_classes.keys():
        raise ValueError('invalid exchange')

    chosen_exchange = exchange_classes[args.exchange]()

    # Initialize the strategy API
    strategy_api = strategy.StrategyAPI(chosen_exchange, args.pair, args.period, args.volume,
                                        comission=0.001, live=0)

    # Initialize the strategy
    chosen_strategy = strategy_classes[args.strategy](strategy_api, **vars(args))

    # Candle interval
    # period = parse_period(args.period)

    while run:
        start_time = time.time()

        new_strategy = chosen_strategy.run()

        if new_strategy:
            chosen_strategy = new_strategy

        time.sleep(args.refresh - (time.time() - start_time))

        strategy_api._update()


def configure_parsers(parsers, classes):
    for class_name, class_value in classes.items():
        parser = parsers.add_parser(class_name)
        class_value.configure_parser(parser)


def get_classes(base_module, class_super):
    classes = {}

    for module_name, module_value in inspect.getmembers(base_module, inspect.ismodule):
        for class_name, class_value in inspect.getmembers(module_value, inspect.isclass):
            if issubclass(class_value, class_super) and class_value != class_super:
                classes[module_name] = class_value

    return classes


def parse_period(period):
    period_keys = {'1': 1, '5': 5, '15': 15, '30': 30, '60': 60, '240': 240, '1H': 60, '4H': 240}
    return period_keys[period]
