import krakenex
import sys
import pprint

class KrakenError(Exception):
    pass

class OrderRequest:
    def __init__(self, txid, descr):
        self.txid = txid
        self.descr = descr

    def __repr__(self):
        return "OrderRequest: txid: {}, {}".format(self.txid,
                                                   self.descr)

class Order:
    def __init__(self, txid, data):
        self.txid = txid
        self.cost = float(data['cost'])
        self.leverage = data['descr']['leverage']
        self.descr = data['descr']['order']
        self.order_type = data['descr']['ordertype']
        self.pair = data['descr']['pair']
        self.price = float(data['descr']['price'])
        self.price2 = float(data['descr']['price2'])
        self.direction = data['descr']['type']
        self.fee = float(data['fee'])
        self.avg_price = float(data['price'])
        self.close_reason = data['reason']
        self.status = data['status']
        self.volume = float(data['vol'])
        self.volume_exec = float(data['vol_exec'])

    def __repr__(self):
        return """Order: txid: {}, cost: {}, leverage: {}, order_type: {},
    price: {}, price2: {}, direction: {}, fee: {}, avg_price: {}, status: {},
    volume: {}, volume_exec: {}""".format(self.txid, self.cost, self.leverage,
    self.order_type, self.price, self.price2, self.direction, self.fee,
    self.avg_price, self.status, self.volume, self.volume_exec)

class OHLC:
    def __init__(self, data):
        self.time = data[0]
        self.open, self.high, self.low, self.close, self.vwap, self.volume = [float(x) for x in data[1:7]]
        self.count = data[7]

    def __repr__(self):
        return """OHLC: time: {}, open: {}, high: {}, low: {}, close: {}, vwap:
            {}, volume: {}, count: {}""".format(self.time, self.open,
            self.high, self.low, self.close, self.vwap, self.volume,
            self.count)

class Ticker:
    def __init__(self, pair, data):
        self.pair = pair
        self.ask = float(data['a'][0])
        self.bid = float(data['b'][0])
        self.last_price = float(data['c'][0])

    def __repr__(self):
        return """Ticker: pair: {}, ask: {}, bid: {}, last_price:
            {}""".format(self.pair, self.ask, self.bid, self.last_price)

class Balance:
    def __init__(self, pairs):
        self.pairs = {x:float(pairs[x]) for x in pairs}

    def __repr__(self):
        return "\n".join(["{}: {:.5f}".format(x, self.pairs[x]) for x in self.pairs])

class Krakenbot:
    def __init__(self, key_file):
        """
        Initialize the Krakenbot class.

        Parameters
        ---------
        key_file : str
            Path of the key file.
        """

        self.k = krakenex.API()
        self.k.load_key(key_file)

    def get_ohlc(self, pair, interval, since=None):
        """
        Return a list of objects containing the OHLC data.

        Parameters
        ---------
        pair : str
            Trading pair.

        interval : int
            Time frame interval in minutes.

        since : int, optional
            Return committed OHLC data since given time.

        Returns
        ------
        list
            List of :obj:`OHLC` objects containing the OHLC data.
        """

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
        """
        Return the last time frame available.

        Parameters
        ----------
        pair : str
            Trading pair.

        interval : int
            Time frame interval in minutes.

        Returns
        -------
        int
            Last time frame available.
        """

        args = {'pair': pair, 'interval': interval}

        try:
            result = self.k.query_public('OHLC', args)
        except:
            raise

        if result['error']:
            raise KrakenError(args, result['error'])

        return result['result']['last']

    def get_average(self, pair, ma, interval):
        """
        Return the average price for the last time frames.

        Parameters
        ----------
        pair : str
            Asset pair.

        ma : int
            Number of intervals to be used in the average.

        interval : int
            Time frame interval in minutes to be used.

        Returns
        -------
        float
           Average.
        """

        try:
            last = self.get_ohlc_last(pair, interval)
        except:
            raise

        start_time = last - ma * 60 * interval

        try:
            ohlc = self.get_ohlc(pair, interval, start_time)
        except:
            raise

        average = 0

        for candle in ohlc:
            average += float(candle.close)

        return average/len(ohlc)

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
            stop-loss-profit-limit (price = stop loss price, price2 = take profit price)
            stop-loss-limit (price = stop loss trigger price, price2 = triggered limit price)
            take-profit-limit (price = take profit trigger price, price2 = triggered limit price)
            trailing-stop (price = trailing stop offset)
            trailing-stop-limit (price = trailing stop offset, price2 = triggered limit offset)
            stop-loss-and-limit (price = stop loss price, price2 = limit price)

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

        if validate:
            return OrderRequest(None, result['result']['descr']['order'])
        else:
            return OrderRequest(result['result']['txid'], result['result']['descr']['order'])

    def query_orders(self, order_ids):
        """
        Read order data.

        Parameters
        ----------
        order_ids : str
            Comma delimited list of ids to be queried.

        Returns
        -------
        list
            List of :obj:`Order` objects containing the order data.
        """

        args = {'txid': order_ids}

        try:
            result = self.k.query_private('QueryOrders', args)
        except:
            raise

        if result['error']:
            raise KrakenError(args, result['error'])

        return [Order(order, result['result'][order]) for order in result['result']]

    def cancel_order(self, order_id):
        """
        Cancel order from the order book.

        Parameters
        ----------
        order_id : str
            Id of the order to be canceled.
        """

        args = {'txid': order_id}

        try:
            result = self.k.query_private('CancelOrder', args)
        except:
            raise

        if result['error']:
            raise KrakenError(args, result['error'])

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

        args = {'pair': pair}

        try:
            result = self.k.query_public('Ticker', args)
        except:
            raise

        if result['error']:
            raise KrakenError(args, result['error'])

        return Ticker(pair, result['result'][pair])

    def get_price(self, pair):
        """
        Get current price.

        Parameters
        ----------
        pair : str
            Asset pair.

        Returns
        -------
        float
            Price.
        """

        try:
            ticker = self.get_ticker(pair)
        except:
            raise

        return ticker.last_price

    def get_balance(self):
        """
        Get account balance.

        Returns
        -------
        :obj:`Balance`
            :obj:`Balance` object
        """

        try:
            result = self.k.query_private('Balance')
        except:
            raise

        return Balance(result['result'])

    def connect(self):
        """
        Connect the socket.

        This operation is optional. If not used, new connections are made as
        required.
        """

        self.c = krakenex.Connection()
        self.k.set_connection(self.c)

    def close(self):
        """Close the connection."""

        self.c.close()
