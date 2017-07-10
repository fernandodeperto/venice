#!/usr/bin/python3

import sys
import krakenex
import krakenbot
import pprint
import argparse

def main(argv):
    parser = argparse.ArgumentParser(description="cancel order")
    parser.add_argument('order_id', help="order id")

    args = parser.parse_args()

    k = krakenbot.Krakenbot('kraken.key')

    try:
        result = k.cancel_order(args.order_id)
    except Exception as e:
        print("Exception: {}".format(e))

if __name__ == "__main__":
    main(sys.argv[1:])
