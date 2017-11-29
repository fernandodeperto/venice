import argparse
import inspect
import signal
import time
import sys

from decimal import getcontext, setcontext, BasicContext, FloatOperation
from logging import getLogger
from logging.config import fileConfig

import argcomplete

from . import api
from . import connection
from . import strategy

MIN_SLEEP = 5


def main():
    def signal_handler(sig, frame):
        nonlocal run

        logger = getLogger(__name__)
        logger.debug("signal {} received".format(sig))

        run = 0

    # Initialize the API
    exchange_classes = get_classes(api, api.ExchangeAPI)

    parser = argparse.ArgumentParser(description='bot based on a strategy')
    parser.add_argument('-l', '--live', action="store_true", help='enable live mode')
    parser.add_argument('exchange', choices=exchange_classes.keys(), help='exchange to be used')
    parser.add_argument('pair', choices=api.ExchangeAPI.PAIRS, help='asset pair')
    parser.add_argument('capital', type=float, help='available initial capital')
    parser.add_argument('period', choices=api.ExchangeAPI.PERIODS, help='candle period')
    parser.add_argument('refresh', type=int, help='time between updates')

    # Configure the strategies' subparsers
    strategy_parsers = parser.add_subparsers(dest='strategy', title='strategies')
    strategy_parsers.required = True

    strategy_classes = get_classes(strategy, strategy.Strategy)
    configure_parsers(strategy_parsers, strategy_classes)

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    fileConfig('logging.conf')
    logger = getLogger(__name__)

    # Decimal module initialization
    setcontext(BasicContext)
    getcontext().prec = 28
    getcontext().traps[FloatOperation] = 1

    # Basic initialization
    run = 1
    signal.signal(signal.SIGINT, signal_handler)

    if args.exchange not in exchange_classes.keys():
        raise ValueError

    chosen_exchange = exchange_classes[args.exchange]()

    # Initialize the strategy API
    strategy_api = strategy.StrategyAPI(
        chosen_exchange, args.pair, args.period, args.capital, live=args.live)

    # Initialize the strategy
    chosen_strategy = strategy_classes[args.strategy](strategy_api, **vars(args))

    while run:
        start_time = time.time()

        try:
            new_strategy = chosen_strategy.run()

            if new_strategy:
                chosen_strategy = new_strategy

        except Exception:
            logger.exception('error running strategy')

        time.sleep(max(args.refresh - (time.time() - start_time), MIN_SLEEP))

        try:
            strategy_api.update()

        except Exception:
            logger.exception('error updating strategy api')

    # Clean up strategy if necessary
    try:
        chosen_strategy.clean_up()

    except Exception:
        logger.exception('error cleaning up the strategy')

    # Ask current strategy to sell closed buy orders
    try:
        strategy_api.clean_up()

    except Exception:
        logger.exception('error cleaning up the strategy api')


def configure_parsers(parsers, classes):
    for class_name, class_value in classes.items():
        parser = parsers.add_parser(
            class_name, description=class_value.descr_text(), help=class_value.help_text())
        class_value.configure_parser(parser)


def get_classes(base_module, class_super):
    classes = {}

    for module_name, module_value in inspect.getmembers(base_module, inspect.ismodule):
        for class_name, class_value in inspect.getmembers(module_value, inspect.isclass):
            if issubclass(class_value, class_super) and class_value != class_super:
                classes[module_name] = class_value

    return classes
