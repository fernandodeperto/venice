#!/usr/bin/python3

import sys
import krakenex
import krakenbot
import pprint
import argparse

def main(argv):
    parser = argparse.ArgumentParser(description="place an order on Kraken")
    parser.add_argument('-q', '--quote', action='store_true', help="convert volume to quote currency")
    parser.add_argument('-n', '--validate', action='store_true', help="do not place order, just validate arguments")
    parser.add_argument('-v', '--verbose', action='store_true', help="print more messages")

    parser.add_argument('pair', help="asset pair")
    parser.add_argument('direction', choices=['buy', 'sell'], help="order direction")
    parser.add_argument('leverage', choices=['none', '1', '2', '3', '4'], help="leverage level")
    parser.add_argument('volume', type=float, help="number of lots")

    subparsers = parser.add_subparsers(dest='order_type', help="order type")
    subparsers.required = True

    parser_market = subparsers.add_parser('market', help="market order")

    parser_limit = subparsers.add_parser('limit', help="limit order")
    parser_limit.add_argument('price', type=float, help="limit price")

    parser_stop_loss = subparsers.add_parser('stop-loss', help="stop-loss order")
    parser_stop_loss.add_argument('price', type=float, help="stop loss price")

    parser_take_profit = subparsers.add_parser('take-profit', help="take-profit order")
    parser_take_profit.add_argument('price', type=float, help="take profit price")

    parser_stop_loss_limit = subparsers.add_parser('stop-loss-limit', help="stop-loss-limit order")
    parser_stop_loss_limit.add_argument('price', type=float, help="stop loss price")
    parser_stop_loss_limit.add_argument('price2', type=float, help="limit price")

    parser_trailing_stop = subparsers.add_parser('trailing-stop', help="trailing-stop order")
    parser_trailing_stop.add_argument('price', help="price offset")

    args = parser.parse_args()

    k = krakenbot.Krakenbot('kraken.key')

    if args.quote:
        volume /= k.get_price(args.pair)

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
        order_request = k.add_order(args.pair, args.direction, args.order_type, args.volume, price=price,
                             price2=price2, leverage=args.leverage, validate=args.validate)
    except Exception as e:
        print("Exception: {}:".format(e))
    else:
        if args.verbose:
            print(order_request)
        else:
            print(order_request.txid)

if __name__ == "__main__":
    main(sys.argv[1:])
