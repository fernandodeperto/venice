#!/usr/bin/python3

import sys
import krakenex
import krakenbot
import pprint

def print_usage():
    print("usage: ./order.py <pair> <direction> <leverage> <volume> market ")
    print("usage: ./order.py <pair> <direction> <leverage> <volume> limit <price>")
    print("usage: ./order.py <pair> <direction> <leverage> <volume> stop-loss <price>")
    print("usage: ./order.py <pair> <direction> <leverage> <volume> take-profit <price>")
    print("usage: ./order.py <pair> <direction> <leverage> <volume> stop-loss-and-limit <stop_price> <limit_price>")
    print("usage: ./order.py <pair> <direction> <leverage> <volume> trailing-stop <offset>")

def main(argv):
    if len(argv) < 5:
        print_usage()
        sys.exit()

    pair, direction, leverage, volume, order_type = argv[0:5]

    if order_type == 'market':
        price = 0
        price2 = 0

    elif order_type in ['limit', 'stop-loss', 'take-profit', 'trailing-stop']:
        if len(argv) < 4:
            print_usage()
            sys.exit()

        price = argv[5]
        price2 = 0

    else:
        if len(argv) < 5:
            print_usage()
            sys.exit()

        price, price2 = argv[5:7]

    k = krakenex.API()
    k.load_key("kraken.key")

    result = krakenbot.add_order(k, pair, direction, order_type, volume, price=price, price2=price2, leverage=leverage)

    if result['error']:
        print("\n".join(result['error']))

    elif result['result']:
        print(result['result']['descr']['order'])
        print("\n".join(result['result']['txid']))

if __name__ == "__main__":
    main(sys.argv[1:])
