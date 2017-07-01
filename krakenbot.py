import krakenex
import sys
import pprint

class KrakenError(Exception):
    def __init__(self, request, errors):
        self.request = request
        self.errors = errors

class Order:
    def __init__(self, txid, data):
        self.txid = txid
        self.cost = data['cost']
        self.leverage = data['descr']['leverage']
        self.descr = data['descr']['order']
        self.order_type = data['descr']['ordertype']
        self.pair = data['descr']['pair']
        self.price = data['descr']['price']
        self.price2 = data['descr']['price2']
        self.direction = data['descr']['type']
        self.fee = data['fee']
        self.avg_price = data['price']
        self.close_reason = data['reason']
        self.status = data['status']
        self.volume = data['vol']
        self.volume_exec = data['vol_exec']

    def __repr__(self):
        return "Order: txid: {}, cost: {}, leverage: {}, order_type: {}, price: {}, price2: {}, direction: {}, fee: {}, avg_price: {}, status: {}, volume: {}, volume_exec: {}".format(self.txid,
                                                                                                                                                                                       self.cost,
                                                                                                                                                                                       self.leverage,
                                                                                                                                                                                       self.order_type,
                                                                                                                                                                                       self.price,
                                                                                                                                                                                       self.price2,
                                                                                                                                                                                       self.direction,
                                                                                                                                                                                       self.fee,
                                                                                                                                                                                       self.avg_price,
                                                                                                                                                                                       self.status,
                                                                                                                                                                                       self.volume,
                                                                                                                                                                                       self.volume_exec)

class OHLC:
    def __init__(self, data):
        self.time = data[0]
        self.open, self.high, self.low, self.close, self.vwap, self.volume = [float(x) for x in data[1:7]]
        self.count = data[7]

    def __repr__(self):
        return "OHLC: time: {}, open: {}, high: {}, low: {}, close: {}, vwap: {}, volume: {}, count: {}".format(self.time,
                                                                                                                self.open,
                                                                                                                self.high,
                                                                                                                self.low,
                                                                                                                self.close,
                                                                                                                self.vwap,
                                                                                                                self.volume,
                                                                                                                self.count)
# a = ask array(<price>, <whole lot volume>, <lot volume>),
# b = bid array(<price>, <whole lot volume>, <lot volume>),
# c = last trade closed array(<price>, <lot volume>),
# v = volume array(<today>, <last 24 hours>),
# p = volume weighted average price array(<today>, <last 24 hours>),
# t = number of trades array(<today>, <last 24 hours>),
# l = low array(<today>, <last 24 hours>),
# h = high array(<today>, <last 24 hours>),
# o = today's opening price
class Ticker:
    def __init__(self, pair, data):
        self.pair = pair
        self.ask = float(data['a'][0])
        self.bid = float(data['b'][0])
        self.last_price = float(data['c'][0])

    def __repr__(self):
        return "Ticker: pair: {}, ask: {}, bid: {}, last_price: {}".format(self.pair,
                                                                           self.ask,
                                                                           self.bid,
                                                                           self.last_price)

class Krakenbot:
    def __init__(self, key_file):
        self.k = krakenex.API()
        self.k.load_key(key_file)

    # <time>, <open>, <high>, <low>, <close>, <vwap>, <volume>, <count>
    def get_ohlc(self, pair, interval, since=None):
        args = {'pair': pair, 'interval': interval}

        if since:
            args['since'] = since

        try:
            result = self.k.query_public('OHLC', args)
        except:
            raise

        if result['error']:
            raise KrakenError(args, result['error'])

        return [OHLC(entry) for entry in result['result'][pair]]

    def get_ohlc_last(self, pair, interval):
        args = {'pair': pair, 'interval': interval}

        try:
            result = self.k.query_public('OHLC', args)
        except:
            raise

        if result['error']:
            raise KrakenError(args, result['error'])

        return result['result']['last']

    def get_average(self, pair, ma, interval):
        try:
            last = self.get_ohlc_last(pair, interval)
        except KrakenError:
            raise

        start_time = last - ma * 60 * interval

        try:
            ohlc = self.get_ohlc(pair, interval, start_time)
        except KrakenError:
            raise

        average = 0

        for candle in ohlc:
            average += float(candle.close)

        return average/len(ohlc)

    #viqc = volume in quote currency (not available for leveraged orders)
    #fcib = prefer fee in base currency
    #fciq = prefer fee in quote currency
    #nompp = no market price protection
    def add_order(self, pair, direction, order_type, volume, price=0, price2=0,
                  leverage='none', flags=[''], validate=False):
        args = {
            'pair': pair,
            'type': direction,
            'ordertype': order_type,
            'volume': volume,
            'price': price,
            'price2': price2,
            'leverage': leverage,
            'flags': flags,
        }

        if validate:
            args['validate'] = 'yes'

        try:
            result = self.k.query_private('AddOrder', args)
        except:
            raise

        if result['error']:
            raise KrakenError(args, order['error'])

        if not validate:
            return result['txid']

    def query_orders(self, order_ids):
        args = {'txid': order_ids}

        try:
            result = self.k.query_private('QueryOrders', args)
        except:
            raise

        if result['error']:
            raise KrakenError(args, result['error'])

        return [Order(order, result['result'][order]) for order in result['result']]

    def cancel_order(self, order_id):
        args = {'txid': order_id}

        try:
            result = self.k.query_private('CancelOrder', args)
        except:
            raise

        if result['error']:
            raise KrakenError(args, result['error'])

    def get_ticker(self, pair):
        args = {'pair': pair}

        try:
            result = self.k.query_public('Ticker', args)
        except:
            raise

        if result['error']:
            raise KrakenError(args, result['error'])

        return Ticker(pair, result['result'][pair])

    def get_price(self, pair):
        try:
            ticker = self.get_ticker(pair)
        except KrakenError:
            raise

        return ticker.last_price

    def connect(self):
        self.c = krakenex.Connection()
        self.k.set_connection(self.c)

    def close(self):
        self.c.close()
