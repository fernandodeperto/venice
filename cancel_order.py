#!/usr/bin/python3

import sys
import krakenex
import krakenbot
import pprint

def print_usage():
    print("usage: ./cancel_order.py <order_id>")

def main(argv):
    if not len(argv):
        print_usage()
        sys.exit()

    order_id = argv[0]

    k = krakenbot.Krakenbot('kraken.key')

    result = k.cancel_order(order_id)

    print(result['result']['count'])

if __name__ == "__main__":
    main(sys.argv[1:])
