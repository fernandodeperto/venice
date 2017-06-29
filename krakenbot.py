import krakenex

class Krakenbot:
    def __init__(self, key_file):
        self.k = krakenex.API()
        self.k.load_key(key_file)

    def get_ohlc(self, pair, interval, since=None):
        args = {'pair': pair, 'interval': interval}

        if since:
            args['since'] = since

        return self.k.query_public('OHLC', args)

    def get_ohlc_last(self, pair, interval):
        result = self.get_ohlc(pair, interval)

        if result['result']:
            return result['result']['last']

    def get_average(self, pair, ma, interval):
        last = self.get_ohlc_last(pair, interval)

        if not last:
            return

        start_time = last - ma * 60 * interval
        ohlc = self.get_ohlc(pair, interval, start_time)

        if ohlc['error']:
            return

        average = 0

        for candle in ohlc['result'][pair]:
            average += float(candle[4])

        return average/len(ohlc['result'][pair])

    def add_order(self, pair, direction, order_type, volume, price=None, price2=None,
                  leverage=None, flags=None, validate=False):
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

        order = self.k.query_private('AddOrder', args)

        return order

    def query_orders(self, order_ids):
        orders = self.k.query_private('QueryOrders', {'txid': order_ids})
        return orders

    def cancel_order(self, order_id):
        result = self.k.query_private('CancelOrder', {'txid': order_id})
        return result

    def connect(self):
        self.c = krakenex.Connection()
        self.k.set_connection(self.c)

    def close(self):
        self.c.close()
