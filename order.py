#!/usr/bin/python3

import sys
import krakenex
import krakenbot
import pprint
import http

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

    pair, direction, leverage = argv[0:3]
    volume = float(argv[3])
    order_type = argv[4]

    k = krakenbot.Krakenbot('kraken.key')

    if direction == 'buy':
        volume /= k.get_price(pair)

    if order_type == 'market':
        price = 0
        price2 = 0

    elif order_type in ['limit', 'stop-loss', 'take-profit', 'trailing-stop']:
        if len(argv) < 4:
            print_usage()
            sys.exit()

        price = float(argv[5])
        price2 = 0

    else:
        if len(argv) < 5:
            print_usage()
            sys.exit()

        price, price2 = [float(x) for x in argv[5:7]]

    try:
        result = k.add_order(pair, direction, order_type, volume, price=price,
                             price2=price2, leverage=leverage)
    except http.client.HTTPException as e:
        print("HTTPException: {}:".format(e))
    except krakenbot.KrakenError as e:
        print("Krakenerror: {}".format(e))
    else:
        print("\n".join(result))

if __name__ == "__main__":
    main(sys.argv[1:])
