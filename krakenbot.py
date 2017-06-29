#!/usr/bin/python3

import krakenex

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

def query_orders(k, txids):
    orders = k.query_private('QueryOrders', {'txid': txids})

    if orders['error']:
        for error in order['error']:
            print(error)

    else:
        return orders['result']
