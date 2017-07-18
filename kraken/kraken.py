import json
import time

import hashlib
import hmac
import base64

import http.client

import urllib.request
import urllib.parse
import urllib.error

import kraken.connection

NONCE_MULTIPLIER = 1000


class KrakenError(Exception):
    pass


class OrderRequest:
    def __init__(self, txids, descr):
        self.txids = txids
        self.descr = descr

    def __str__(self):
            return self.descr


class Order:
    def __init__(self, txid, closetm, cost, descr, expiretm, fee, misc, oflags,
                 opentm, price, reason, refid, starttm, userref, vol, vol_exec,
                 status=None, stopprice=None):

        self.txid = txid
        self.closetm = closetm
        self.cost = cost
        self.descr = OrderInfo(**descr)
        self.expiretm = expiretm
        self.fee = fee
        self.misc = misc
        self.oflags = oflags
        self.opentm = opentm
        self.price = price
        self.reason = reason
        self.refid = refid
        self.starttm = starttm
        self.status = status
        self.userref = userref
        self.vol = vol
        self.vol_exec = vol_exec

        self.status = status
        self.stopprice = stopprice

    def __str__(self):
        return self.txid


class OrderInfo:
    def __init__(self, pair, type, ordertype, price, price2, leverage,
                 order, close=None):
        """
        Initialize the OrderInfo class.

        Parameters
        ----------
        pair : str
            asset pair

        direction : str
            type of order (buy/sell)

        ordertype : str
            order type

        price : str
            primary price

        price2 : str
            secondary price

        leverage : str
            amount of leverage

        order : str
            order description

        close : str
            conditional close order description (if conditional close set)
        """
        self.pair = pair
        self.direction = type
        self.order_type = ordertype
        self.price = price
        self.price2 = price2
        self.leverage = leverage
        self.order = order
        self.close = close

    def __str__(self):
        return self.order


class OHLC:
    def __init__(self, time, open, high, low, close, vwap, volume, count):
        self.time = time
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.vwap = vwap
        self.volume = volume
        self.count = count

    def __str__(self):
        return '{} O:{}, H:{}, L:{}, C:{}, V:{}'.format(
            self.time, self.open, self.high, self.low, self.close, self.volume)


class Ticker:
    def __init__(self, pair, a, b, c, h, l, o, p, t, v):
        """
        a = ask array(<price>, <whole lot volume>, <lot volume>),
        b = bid array(<price>, <whole lot volume>, <lot volume>),
        c = last trade closed array(<price>, <lot volume>),
        v = volume array(<today>, <last 24 hours>),
        p = volume weighted average price array(<today>, <last 24 hours>),
        t = number of trades array(<today>, <last 24 hours>),
        l = low array(<today>, <last 24 hours>),
        h = high array(<today>, <last 24 hours>),
        o = today's opening price
        """
        self.pair = pair
        self.ask = a[0]
        self.bid = b[0]
        self.last_price = c[0]

    def __str__(self):
        return '{} ask: {}, bid: {}, last_price: {}'.format(
            self.pair, self.ask, self.bid, self.last_price)


class Balance:
    def __init__(self, pairs):
        self.pairs = pairs


class Position:
    def __init__(self, posid, ordertxid, pair, time, type, ordertype, cost, fee, vol, vol_closed,
                 margin, value, net, misc, oflags, rollovertm, terms, posstatus):
        """
        <position_txid> = open position info
            ordertxid = order responsible for execution of trade
            pair = asset pair
            time = unix timestamp of trade
            type = type of order used to open position (buy/sell)
            ordertype = order type used to open position
            cost = opening cost of position (quote currency unless viqc set in oflags)
            fee = opening fee of position (quote currency)
            vol = position volume (base currency unless viqc set in oflags)
            vol_closed = position volume closed (base currency unless viqc set in oflags)
            margin = initial margin (quote currency)
            value = current value of remaining position (if docalcs requested.  quote currency)
            net = unrealized profit/loss of remaining position (if docalcs requested.  quote currency, quote currency scale)
            misc = comma delimited list of miscellaneous info
            oflags = comma delimited list of order flags
                viqc = volume in quote currency
        """
        self.posid = posid
        self.txid = ordertxid
        self.pair = pair
        self.time = time
        self.direction = type
        self.order_type = ordertype
        self.cost = cost
        self.fee = fee
        self.vol = vol
        self.vol_closed = vol_closed
        self.margin = margin
        self.value = value
        self.net = net
        self.misc = misc
        self.oflags = oflags
        self.rollovertm = rollovertm
        self.terms = terms
        self.posstatus = posstatus

    def __str__(self):
        return self.position_id


class Kraken:
    def __init__(self, key='', secret=''):
        self.key = key
        self.secret = secret

    def load_key(self, path):
        with open(path, 'r') as f:
            self.key = f.readline().strip()
            self.secret = f.readline().strip()

    def query_orders(self, txids):
        """
        Query orders from the exchange.

        Parameters
        ----------
        txids : list
            list of orders
        """
        request = {'txid': ','.join(txids)}

        try:
            with kraken.connection.KrakenAPI(self.key, self.secret) as k:
                result = k.query_private('QueryOrders', request)
        except:
            raise

        if result['error']:
            raise KrakenError(request, result['error'])

        return [Order(x, **result['result'][x]) for x in result['result']]

    def get_ohlc(self, pair, interval, since=None):
        request = {'pair': pair, 'interval': interval}

        if since:
            request['since'] = since

        try:
            with kraken.connection.KrakenAPI(self.key, self.secret) as k:
                result = k.query_public('OHLC', request)
        except:
            raise

        if result['error']:
            raise KrakenError(request, result['error'])

        return [OHLC(*x) for x in result['result'][pair]]

    def get_ticker(self, pair):
        """
        Get ticker information.

        Parameters
        ----------
        pair : str
            Asset pair.

        Returns
        -------
        :obj:`Ticker`
            Object of the `Ticker` class with the information.
        """

        request = {'pair': pair}

        try:
            with kraken.connection.KrakenAPI(self.key, self.secret) as k:
                result = k.query_public('Ticker', request)
        except:
            raise

        if result['error']:
            raise KrakenError(request, result['error'])

        return Ticker(pair, *result['result'][pair])

    def get_balance(self):
        try:
            with kraken.connection.KrakenAPI(self.key, self.secret) as k:
                result = k.query_private('Balance')
        except:
            raise

        if result['error']:
            raise KrakenError(result['error'])

        return Balance(result['result'])

    def get_positions(self):
        """
        Get open positions.
        """

        try:
            with kraken.connection.KrakenAPI(self.key, self.secret) as k:
                result = k.query_private('OpenPositions', {'docalcs': 'yes'})
        except:
            raise

        if result['error']:
            raise KrakenError(result['error'])

        return [Position(x, **result['result'][x]) for x in result['result']]
