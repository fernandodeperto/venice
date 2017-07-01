#!/usr/bin/python3

import sys
import krakenex
import krakenbot
import pprint
import http

def print_usage():
    print("usage: ./cancel_order.py <order_id>")

def main(argv):
    if not len(argv):
        print_usage()
        sys.exit()

    order_id = argv[0]

    k = krakenbot.Krakenbot('kraken.key')

    try:
        result = k.cancel_order(order_id)
    except http.client.HTTPException as e:
        print("HTTPException: {}:".format(e))
    except krakenbot.KrakenError as e:
        print("Krakenerror: {}".format(e))
    else:
        print("ok")

if __name__ == "__main__":
    main(sys.argv[1:])
