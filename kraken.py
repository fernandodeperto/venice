#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

import sys
import krakenex
import krakenbot
import pprint
import argparse
import argcomplete
import logging
import tabulate

def main(argv):
    parser = argparse.ArgumentParser(description="run commands on the Kraken exchange")
    parser.add_argument('-v', '--verbose', action='store_true', help="print more messages")

    parser_cmd = parser.add_subparsers(dest='cmd', help="command")
    parser_cmd.required = True

    parser_order = parser_cmd.add_parser('order', help="place order")
    parser_order.set_defaults(func=order)
    parser_order.add_argument('-q', '--quote', action='store_true', help="convert volume to quote currency")
    parser_order.add_argument('-n', '--validate', action='store_true', help="do not place order, just validate arguments")
    parser_order.add_argument('pair', help="asset pair")
    parser_order.add_argument('direction', choices=['buy', 'sell'], help="order direction")
    parser_order.add_argument('leverage', choices=['none', '2', '3', '4', '5'], help="leverage level")
    parser_order.add_argument('volume', type=float, help="order volume")

    parser_order_type = parser_order.add_subparsers(dest='order_type', help="order type")
    parser_order_type.required = True

    parser_market = parser_order_type.add_parser('market', help="market order")

    parser_limit = parser_order_type.add_parser('limit', help="limit order")
    parser_limit.add_argument('price', type=float, help="limit price")

    parser_stop_loss = parser_order_type.add_parser('stop-loss', help="stop-loss order")
    parser_stop_loss.add_argument('price', type=float, help="stop loss price")

    parser_take_profit = parser_order_type.add_parser('take-profit', help="take-profit order")
    parser_take_profit.add_argument('price', type=float, help="take profit price")

    parser_stop_loss_limit = parser_order_type.add_parser('stop-loss-limit', help="stop-loss-limit order")
    parser_stop_loss_limit.add_argument('price', type=float, help="stop loss price")
    parser_stop_loss_limit.add_argument('price2', type=float, help="limit price")

    parser_trailing_stop = parser_order_type.add_parser('trailing-stop', help="trailing-stop order")
    parser_trailing_stop.add_argument('price', type=float, help="price offset")

    parser_query = parser_cmd.add_parser('query', help="query orders")
    parser_query.set_defaults(func=query)
    parser_query.add_argument('order_id', help="order id")

    parser_cancel = parser_cmd.add_parser('cancel', help="cancel order")
    parser_cancel.set_defaults(func=cancel)
    parser_cancel.add_argument('order_id', help="order id")

    parser_balance = parser_cmd.add_parser('balance', help="get account balance")
    parser_balance.set_defaults(func=balance)

    parser_open = parser_cmd.add_parser('open', help="get open orders")
    parser_open.set_defaults(func=open)

    parser_closed = parser_cmd.add_parser('closed', help="get closed orders")
    parser_closed.set_defaults(func=closed)
    parser_closed.add_argument('num', type=int, help="number of hours")

    parser_position = parser_cmd.add_parser('position', help="get open positions")
    parser_position.set_defaults(func=position)
    parser_position.add_argument('-p', '--profit', action='store_true', help="include profit data")

    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    args.func(args)


def order(args):
    k = krakenbot.Krakenbot('kraken.key')

    if args.quote:
        if args.order_type == 'market':
            volume = args.volume / k.get_price(args.pair)
        elif args.order_type == 'stop-loss-limit':
            volume = args.volume / args.price2
        elif args.order_type in ['limit', 'stop-loss', 'take-profit']:
            volume = args.volume / args.price
        elif args.order_type == 'trailing-stop':
            volume = args.volume / (k.get_price(args.pair) + args.price)
    else:
        volume = args.volume

    if args.order_type == 'market':
        price = 0
        price2 = 0
    elif args.order_type in ['limit', 'stop-loss', 'take-profit', 'trailing-stop']:
        price = args.price
        price2 = 0
    else:
        price = args.price
        price2 = args.price2

    try:
        order_request = k.add_order(args.pair, args.direction, args.order_type,
                                    volume, price=price, price2=price2,
                                    leverage=args.leverage,
                                    validate=args.validate)
    except Exception as e:
        print("Exception: {}:".format(e))
    else:
        if args.validate:
            print("{}".format(order_request.descr))
        else:
            print("{}: {}".format(", ".join(order_request.txids), order_request.descr))


def query(args):
    k = krakenbot.Krakenbot('kraken.key')

    try:
        result = k.query_orders(args.order_id)
    except Exception as e:
        print("Exception: {}".format(e))
    else:
        print(tabulate.tabulate([['txid', result[0].txid],
                                 ['descr', result[0].info.description],
                                 ['direction', result[0].info.direction],
                                 ['order_type', result[0].info.order_type],
                                 ['price', result[0].info.price],
                                 ['price2', result[0].info.price2],
                                 ['leverage', result[0].info.leverage],
                                 ['cost', result[0].cost],
                                 ['fee', result[0].fee],
                                 ['avg_price', result[0].avg_price],
                                 ['stop_price', result[0].stop_price],
                                 ['status', result[0].status],
                                 ['reason', result[0].reason],
                                 ['volume', result[0].volume],
                                 ['volume_exec', result[0].volume_exec]],
                                headers=['key', 'value']))


def cancel(args):
    k = krakenbot.Krakenbot('kraken.key')

    try:
        k.cancel_order(args.order_id)
    except Exception as e:
        print("Exception: {}".format(e))


def balance(args):
    k = krakenbot.Krakenbot('kraken.key')

    try:
        result = k.get_balance()
    except Exception as e:
        print("Exception: {}".format(e))
    else:
        print(tabulate.tabulate([[x, result.pairs[x]] for x in result.pairs], headers=['pair', 'balance'], floatfmt='.5f'))


def open(args):
    k = krakenbot.Krakenbot('kraken.key')

    try:
        result = k.get_open_orders()
    except Exception as e:
        print("Exception: {}".format(e))
    else:
        print(tabulate.tabulate([[order.txid, order.status, order.volume,
                                  order.volume_exec, order.info.direction,
                                  order.info.order_type, order.info.pair,
                                  order.info.leverage, order.info.price,
                                  order.info.price2] for order in result],
                                headers=['txid', 'status', 'vol', 'vol_exec',
                                         'direction', 'order_type', 'pair',
                                         'leverage', 'price', 'price2']))


def closed(args):
    k = krakenbot.Krakenbot('kraken.key')

    try:
        time = k.get_time()
    except Exception as e:
        print("Exception: {}".format(e))
    else:
        try:
            result = k.get_closed_orders(time - 3600 * args.num - 1)
        except Exception as e:
            print("Exception: {}".format(e))
        else:
            print(tabulate.tabulate([[order.txid, order.status, order.volume,
                                      order.volume_exec, order.info.direction,
                                      order.info.order_type, order.info.pair,
                                      order.info.leverage, order.info.price,
                                      order.info.price2] for order in result],
                                    headers=['txid', 'status', 'vol', 'vol_exec',
                                             'direction', 'order_type', 'pair',
                                             'leverage', 'price', 'price2']))


def position(args):
    k = krakenbot.Krakenbot('kraken.key')

    try:
        result = k.get_open_positions(args.profit)
    except Exception as e:
        print("Exception: {}".format(e))
    else:
        print(tabulate.tabulate([[position.position_id, position.cost,
                                  position.fee, position.margin,
                                  position.profit, position.order_type,
                                  position.pair, position.status,
                                  position.direction, position.volume,
                                  position.volume_closed]
                                 for position in result],
                                headers=['posid', 'cost', 'fee', 'margin',
                                         'profit', 'order_type', 'pair',
                                         'status', 'direction', 'volume',
                                         'volume_closed']))


if __name__ == "__main__":
    main(sys.argv[1:])
