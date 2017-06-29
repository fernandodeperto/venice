import krakenex

def get_ohlc(k, pair, interval, since=None):
    args = {'pair': pair, 'interval': interval}

    if since:
        args['since'] = since

    return k.query_public('OHLC', args)

def get_ohlc_last(k, pair, interval):
    result = get_ohlc(k, pair, interval)

    if result['result']:
        return result['result']['last']

def get_average(k, pair, ma, interval):
    last = get_ohlc_last(k, pair, interval)

    if not last:
        return

    start_time = last - ma * 60 * interval

    ohlc = get_ohlc(k, pair, interval, start_time)

    if ohlc['error']:
        return

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

    return order

def query_orders(k, order_ids):
    orders = k.query_private('QueryOrders', {'txid': order_ids})
    return orders

def cancel_order(k, order_id):
    result = k.query_private('CancelOrder', {'txid': order_id})
    return result
