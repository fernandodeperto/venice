#!/usr/bin/python3

import sys
import krakenex
import krakenbot
import pprint
import http

def main(argv):
    k = krakenbot.Krakenbot('kraken.key')

    try:
        result = k.get_balance()
    except http.client.HTTPException as e:
        print("HTTPException: {}:".format(e))
    except krakenbot.KrakenError as e:
        print("Krakenerror: {}".format(e))
    else:
        pprint.pprint(result)

if __name__ == "__main__":
    main(sys.argv[1:])
