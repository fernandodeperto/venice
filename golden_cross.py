#!/usr/bin/python3

import sys
import signal
import krakenex
import krakenbot
import getopt
import pprint
import http
import logging
import time

def print_usage():
    print("usage: ./golden_cross.py <eth> <eur> <ma1> <ma2> <interval>")

def main(argv):
    refresh_rate = 10
    run = 1
    pair = 'XETHZEUR'

    logFormatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    fileHandler = logging.FileHandler('golden_cross.log')
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)

    def get_average(ma):
        average = None

        while run:
            try:
                average = k.get_average(pair, ma, interval)
            except http.client.HTTPException as e:
                logger.warning("HTTPException: {}".format(e))
            except krakenbot.KrakenError as e:
                logger.warning("Krakenerror: {}".format(e))
            else:
                return average

    def print_status():
        logger.info("average1: {:.5f}, average2: {:.5f}, eth: {:.5f}, eur: {:.5f}".format(average1, average2, eth, eur))

    def confirm_orders(txids):
        nonlocal eth, eur

        try:
            orders = k.query_orders(", ".join(txids))
        except http.client.HTTPException as e:
            logger.warning("HTTPException: {}".format(e))
        except krakenbot.KrakenError as e:
            logger.warning("Krakenerror: {}".format(e))
        else:
            remaining_orders = []

            for order in orders:
                if order.status in ['closed', 'canceled']:
                    if order.direction == 'buy':
                        eth += order.volume_exec
                    else:
                        eur += order.cost - order.fee

                elif order.status in ['pending', 'open']:
                    remaining_orders.append(order.txid)

            return remaining_orders

    def signal_handler(signal, frame):
        nonlocal run
        run = 0

    signal.signal(signal.SIGINT, signal_handler)

    if len(argv) < 5:
        print_usage()
        sys.exit(2)

    eth, eur = [float(x) for x in argv[0:2]]
    ma1, ma2, interval = [int(x) for x in argv[2:5]]

    k = krakenbot.Krakenbot('kraken.key')

    pending_orders = []

    while run:
        average1, average2 = [get_average(x) for x in [ma1, ma2]]
        print_status()

        if pending_orders:
            pending_orders = confirm_orders(pending_orders)

        # Sell
        if average1 <= average2 and eth:
            try:
                result = k.add_order(pair, 'sell', 'market', eth)
            except http.client.HTTPException as e:
                logger.warning("HTTPException: {}".format(e))
            except krakenbot.KrakenError as e:
                logger.warning("Krakenerror: {}".format(e))
            else:
                logger.info(result)

                eth = 0
                pending_orders += result.txid

        # Buy
        elif average1 > average2 and eur:
            try:
                price = k.get_price(pair)
            except http.client.HTTPException as e:
                logger.warning("HTTPException: {}".format(e))
            except krakenbot.KrakenError as e:
                logger.warning("Krakenerror: {}".format(e))
            else:
                try:
                    result = k.add_order(pair, 'buy', 'market', eur/price)
                except http.client.HTTPException as e:
                    logger.warning("HTTPException: {}".format(e))
                except krakenbot.KrakenError as e:
                    logger.warning("Krakenerror: {}".format(e))
                else:
                    logger.info(result)

                    eur = 0
                    pending_orders += result.txid

        time.sleep(refresh_rate)

if __name__ == "__main__":
    main(sys.argv[1:])
