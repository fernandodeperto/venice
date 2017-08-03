from .connection import KrakenConnection

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
        self.time = int(time)
        self.open = float(open)
        self.high = float(high)
        self.low = float(low)
        self.close = float(close)
        self.vwap = float(vwap)
        self.volume = float(volume)
        self.count = int(count)

    def __str__(self):
        return '{} O:{}, H:{}, L:{}, C:{}, V:{}'.format(
            self.time, self.open, self.high, self.low, self.close, self.volume)


class Ticker:
    def __init__(self, pair, a, b, c):
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
        self.ask = float(a[0])
        self.bid = float(b[0])
        self.last_price = float(c[0])

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
        return self.posid


class AssetInfo:
    def __init__(self, asset, display_decimals, altname, aclass, decimals):
        self.asset = asset
        self.display_decimals = display_decimals
        self.altname = altname
        self.aclass = aclass
        self.decimals = decimals

    def __str__(self):
        return self.asset


class KrakenAPI:
    def __init__(self, key='', secret=''):
        self.key = key
        self.secret = secret

    def load_key(self, path):
        with open(path, 'r') as key_file:
            self.key = key_file.readline().strip()
            self.secret = key_file.readline().strip()

    @staticmethod
    def get_server_time():
        try:
            with KrakenConnection() as k:
                result = k.query_public('Time')
        except:
            raise

        if result['error']:
            raise KrakenError(result['error'])

        return result['result']['unixtime']

    @staticmethod
    def get_assets_info(assets):
        request = {'asset': ','.join(assets)}

        try:
            with KrakenConnection() as k:
                result = k.query_public('Assets', request)
        except:
            raise

        if result['error']:
            raise KrakenError(request, result['error'])

        return [AssetInfo(x, **result['result'][x]) for x in result['result']]

    @staticmethod
    def get_ticker(pair):
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

        try:
            with KrakenConnection() as k:
                result = k.query_public('Ticker', {'pair': pair})
        except:
            raise

        if result['error']:
            raise KrakenError(result['error'])

        return Ticker(pair, *result['result'][pair])

    @staticmethod
    def get_ohlc(pair, interval, since=None):
        """
        Get OHLC data.

        Parameters
        ----------

        pair : str
            Asset pair.

        interval : int
            Interval in minutes.

            Allowed values: 1 (default), 5, 15, 30, 60, 240, 1440, 10080, 21600

        since : int
            Timestamp of the first candle to be included.

        Returns
        -------
        list
            List of :obj:`OHLC` objects containing the OHL data.
        """
        request = {'pair': pair, 'interval': interval}

        if since:
            request['since'] = since

        try:
            with KrakenConnection() as k:
                result = k.query_public('OHLC', request)
        except:
            raise

        if result['error']:
            raise KrakenError(request, result['error'])

        return [OHLC(*x) for x in result['result'][pair]]

    def get_balance(self):
        try:
            with KrakenConnection(self.key, self.secret) as k:
                result = k.query_private('Balance')
        except:
            raise

        if result['error']:
            raise KrakenError(result['error'])

        return Balance(result['result'])

    def get_positions(self):

        try:
            with KrakenConnection(self.key, self.secret) as k:
                result = k.query_private('OpenPositions', {'docalcs': 'yes'})
        except:
            raise

        if result['error']:
            raise KrakenError(result['error'])

        return [Position(x, **result['result'][x]) for x in result['result']]

    def get_open_orders(self):
        try:
            with KrakenConnection(self.key, self.secret) as k:
                result = k.query_private('OpenOrders')
        except:
            raise

        if result['error']:
            raise KrakenError(result['error'])

        return [Order(order, **result['result']['open'][order])
                for order in result['result']['open']]

    def get_closed_orders(self, time):
        """
        Get closed orders from a timestamp.

        Parameters
        ----------
        time : str
            UNIX timestamp

        Returns
        -------
        list
            List of :obj:`Order` objects containing the closed orders.
        """

        try:
            with KrakenConnection(self.key, self.secret) as k:
                result = k.query_private('ClosedOrders', {'start': time})
        except:
            raise

        if result['error']:
            raise KrakenError(result['error'])

        return [Order(order, **result['result']['closed'][order])
                for order in result['result']['closed']]

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
            with KrakenConnection(self.key, self.secret) as k:
                result = k.query_private('QueryOrders', request)
        except:
            raise

        if result['error']:
            raise KrakenError(request, result['error'])

        return [Order(x, **result['result'][x]) for x in result['result']]

    def add_order(self, pair, direction, order_type, volume, price=0, price2=0,
                  leverage='none', flags=[''], validate=False):
        """
        Add an order to the order book.

        Parameters
        ----------
        pair : str
            Asset pair.
        direction : str
            Direction of the order, can be 'buy' or 'sell'.
        order_type : str
            Type of the order, can be:

            market
            limit (price = limit price)
            stop-loss (price = stop loss price)
            take-profit (price = take profit price)
            stop-loss-profit (price = stop loss price, price2 = take profit price)
            stop-loss-and-limit (price = stop loss price, price2 = limit price)
            trailing-stop (price = trailing stop offset)

        volume : float
            Number of lots in the quote currency.

        price : float
            Main price of the order.

        price2 : float
            Secondary price of the order.

        leverage : str
            Margin to be used in the order.

        flags : list
            List of flags to be included in the order, can be:

            viqc = volume in quote currency (not available for leveraged orders)
            fcib = prefer fee in base currency
            fciq = prefer fee in quote currency
            nompp = no market price protection
            post = post only order (available when ordertype = limit)

        validate : str
            Flag used to only validate the order, and not add it to the book.

        Returns
        -------
        :obj:`OrderRequest`
            `OrderRequest` object containing the request data.
        """

        request = {
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
            request['validate'] = 'yes'

        try:
            with KrakenConnection(self.key, self.secret) as k:
                result = k.query_private('AddOrder', request)
        except:
            raise

        if result['error']:
            raise KrakenError(request, result['error'])

        if validate:
            return OrderRequest(None, result['result']['descr']['order'])

        return OrderRequest(result['result']['txid'], result['result']['descr']['order'])
