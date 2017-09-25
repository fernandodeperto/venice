import argparse
import collections
import importlib
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
    parser.add_argument('pair', help='asset pair')
    parser.add_argument('volume', type=float, help='main currency volume')
    parser.add_argument('volume2', type=float, help='quote currency volume')
    parser.add_argument('interval', help='candle interval')
    parser.add_argument('refresh', type=int, help='time between updates')

    # Configure the strategies' subparsers
    strategy_parsers = parser.add_subparsers(dest='strategy', title='strategies')
    strategy_classes = get_classes(strategy, strategy.Strategy)
    configure_parsers(strategy_parsers, strategy_classes)

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger()

    # Basic initialization
    run = 1
    signal.signal(signal.SIGINT, signal_handler)

    # Initialize the API
    api_classes = get_classes(api, api.ExchangeAPI)

    if args.exchange not in api_classes.keys():
        raise ValueError('invalid exchange')

    chosen_api = api_classes[args.exchange]()

    # Initialize the strategy
    chosen_strategy = strategy_classes[args.strategy](**vars(args))

    # Candle interval
    interval = parse_interval(args.interval)

    if not interval:
        raise ValueError('invalid interval', args.interval)

    sys.exit()

    while run:
        start_time = time.time()

        """
        Notes on the interface between the main code, the strategy and the API.

        - the strategy should be able to return a list of order requests, including:
          - place order(name, type + arguments)
          - cancel order(name)
        - the strategy should not have direct access to the API or the orders
        - one possibility is for the strategy to not even know how much money is being manipulates,
        instead just placing and cancelling contracts. in this case, the main code informs the
        strategy how many contracts it can use. another possibility is to inform the strategy the
        volume it can use on both currencies, and it places orders in terms of the volume, and not
        contracts
        - there's also two different approaches with regard to the orders: allowing and nont
        allowing short orders. not allowing short orders means that the strategy can only
        buy and sell
        """

        # chosen_strategy.run()

        time.sleep(args.refresh - (time.time() - start_time))

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

def parse_interval(interval):
    keys = {
        '1': 1, '5': 5, '15': 15, '30': 30, '60': 60, '240': 240,
        '1H': 60, '4H': 240}

    if interval in keys:
        return keys[interval]
