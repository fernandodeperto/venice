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

from . import strategy

StrategyModule = collections.namedtuple(
    'StrategyModule',
    'module_name class_name value')

def main():
    def signal_handler(sig, frame):
        nonlocal run
        run = 0

    parser = argparse.ArgumentParser(description='bot based on a strategy')
    parser.add_argument('-l', '--live', action='store_true', help="enable trade mode")
    parser.add_argument('exchange', help='exchange to be used')
    parser.add_argument('pair', help='asset pair')
    parser.add_argument('volume', type=float, help='main currency volume')
    parser.add_argument('volume2', type=float, help='quote currency volume')
    parser.add_argument('interval', help='candle interval')
    parser.add_argument('refresh', type=int, help='time between updates')

    strategy_parsers = parser.add_subparsers(help='strategy help')

    # Configure the strategies' subparsers
    classes = strategy_classes()

    for class_name, class_value in classes:
        strategy_parser = strategy_parsers.add_parser(class_name, help=class_value.help_text())
        class_value.configure_parser(strategy_parser)

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger()

    run = 1
    signal.signal(signal.SIGINT, signal_handler)

def main2():
    interval = parse_interval(args.interval)

    if not interval:
        raise ValueError('invalid interval', args.interval)

    strategy = load_module(args.strategy).value()

def strategy_classes():
    classes = []

    for module_name, module_value in inspect.getmembers(strategy, inspect.ismodule):
        for class_name, class_value in inspect.getmembers(module_value, inspect.isclass):
            if issubclass(class_value, strategy.strategy.Strategy) and class_value != strategy.strategy.Strategy:
                classes.append((module_name, class_value))

    return classes

def parse_interval(interval):
    keys = {
        '1': 1, '5': 5, '15': 15, '30': 30, '60': 60, '240': 240,
        '1H': 60, '4H': 240}

    if interval in keys:
        return keys[interval]
