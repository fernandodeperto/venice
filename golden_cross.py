#!/usr/bin/python3

import sys, getopt
import krakenex
import pprint
import statistics
import signal
import time

def main(argv):
    eth = 0
    eur = 0
    ma1 = 10
    ma2 = 21
    interval = 5
    refresh_rate = 5

    run = 1

    def signal_handler(signal, frame):
        nonlocal run
        run = 0

    signal.signal(signal.SIGINT, signal_handler)

    try:
        opts, args = getopt.getopt(argv,"hr",["eth=", "eur=", "ma1=", "ma2=", "interval=", "refresh="])

    except getopt.GetoptError:
        print('golden_cross.py --eth ETH --eur EUR --ma1 MA1 --ma2 MA2 --interval INTERVAL')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('golden_cross.py --eth ETH --eur EUR --ma1 MA1 --ma2 MA2 --interval INTERVAL')
            sys.exit()

        elif opt == "--eth":
            eth = arg

        elif opt == "--eur":
            eur = arg

        elif opt == "--ma1":
            ma1 = arg

        elif opt == "--ma2":
            ma2 = arg

        elif opt == "--interval":
            interval = arg

        elif opt in ["r", "--refresh"]:
            refresh_rate = arg

    k = krakenex.API()
    k.load_key('kraken.key')

    #txids = add_order(k, 'XETHZEUR', 'sell', 'limit', volume=0.01, price = 300)
    #for txid in txids:
    #    print(txid)

    bull = False

    averages = [get_average(k, 'XETHZEUR', ma1, interval), get_average(k, 'XETHZEUR', ma2, interval)]
    if average[0] > average[1]:
        bull = True

    while(run):
        averages = [get_average(k, 'XETHZEUR', ma1, interval), get_average(k, 'XETHZEUR', ma2, interval)]
        print("averages: %.2f, %.2f" % (averages[0], averages[1]))

        # Sell
        if bull and average[0] <= average[1]:
            txids = add_order(k, 'XETHZEUR', 'sell', 'market', volume=eth)
            if txids:
                for txid in txids:
                    print(txid)

                bull = False
                eth = 0
                #TODO Get amount used

        # Buy
        elif not bull and average[0] > average[1]:
            txids = add_order(k, 'XETHZEUR', 'buy', 'market', volume=eur)
            if txids:
                for txid in txids:
                    print(txid)

                bull = True
                eur = 0
                #TODO Get amount used

        time.sleep(refresh_rate)

def get_ohlc(k, pair, interval, since=None):
    if since:
        return k.query_public('OHLC', {'pair': pair, 'interval': interval, 'since': since})

    else:
        return k.query_public('OHLC', {'pair': pair, 'interval': interval})

def get_ohlc_last(k, pair, interval):
    ohlc = get_ohlc(k, pair, interval, None)
    return ohlc['result']['last']

def get_average(k, pair, ma, interval):
    last = get_ohlc_last(k, pair, interval)
    start_time = last - ma * 60 * interval
    ohlc = get_ohlc(k, pair, interval, start_time)

    average = 0

    for candle in ohlc['result'][pair]:
        average += float(candle[4])

    return average/len(ohlc['result'][pair])

def add_order(k, pair, direction, order_type, volume, price=None, price2=None, leverage=None, flags=None, validate=False):
    args = {
        'pair': pair,
        'type': direction,
        'ordertype': order_type,
        'volume': volume
    }

    if price:
        args['price'] = price

    if price2:
        args['price2'] = price2

    if leverage:
        args['leverage'] = leverage

    if flags:
        args['oflags'] = flags

    if validate:
        args['validate'] = True

    order = k.query_private('AddOrder', args)

    if order['error']:
        for error in order['error']:
            print(error)

    else:
        print(order['result']['descr']['order'])
        return order['result']['txid']

if __name__ == "__main__":
    main(sys.argv[1:])
