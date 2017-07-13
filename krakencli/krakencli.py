import krakenex


DEFAULT_PRECISION = 5


class KrakenError(Exception):
    pass


class OrderRequest:
    def __init__(self, txids, descr):
        self.txids = txids
        self.descr = descr


def __str__(self):
        return self.descr


class OrderInfo:
    def __init__(self, descr):
        """
        Initialize the OrderInfo class.

        Parameters
        ----------
        descr : dict
            Dictionary containing the following information:

            pair = asset pair
            type = type of order (buy/sell)
            ordertype = order type (See Add standard order)
            price = primary price
            price2 = secondary price
            leverage = amount of leverage
            order = order description
            close = conditional close order description (if conditional close set)
        """

        self.description = descr['order']
        self.order_type = descr['ordertype']
        self.pair = descr['pair']
        self.leverage = descr['leverage']
        self.direction = descr['type']
        self.price = float(descr['price'])
        self.price2 = float(descr['price2'])

        if 'close' in descr:
            self.close = descr['close']
        else:
            self.close = None

    def __str__(self):
        return self.description


class Order:
    def __init__(self, txid, data):
        self.txid = txid
        self.info = OrderInfo(data['descr'])
        self.cost = float(data['cost'])
        self.fee = float(data['fee'])
        self.avg_price = float(data['price'])
        self.status = data['status']
        self.volume = float(data['vol'])
        self.volume_exec = float(data['vol_exec'])

        if 'stopprice' in data:
            self.stop_price = data['stopprice']
        else:
            self.stop_price = None

        if self.status in ['closed', 'canceled']:
            self.reason = data['reason']
        else:
            self.reason = None

    def __str__(self):
        return self.txid


class OHLC:
    def __init__(self, data):
        self.time = int(data[0])
        self.open, self.high, self.low, self.close, self.vwap, self.volume = [float(x) for x in data[1:7]]
        self.count = data[7]

    def __str(self):
        return "{} O:{}, H:{}, L:{}, C:{}, V:{}".format(self.time, self.open,
                                                        self.high, self.low,
                                                        self.close, self.volume)


class Ticker:
    def __init__(self, pair, data):
        self.pair = pair
        self.ask = float(data['a'][0])
        self.bid = float(data['b'][0])
        self.last_price = float(data['c'][0])


class Balance:
    def __init__(self, pairs):
        self.pairs = {x: float(pairs[x]) for x in pairs}


class Position:
    def __init__(self, posid, position):
        """
        Initialize the Position object.

        Parameters
        ----------
        posid : str
            Position ID.

        position : dict
            Dictionary containing the position data.

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

        self.position_id = posid
        self.cost = float(position['cost'])
        self.fee = float(position['fee'])
        self.margin = float(position['margin'])
        self.txid = position['ordertxid']
        self.order_type = position['ordertype']
        self.pair = position['pair']
        self.status = position['posstatus']
        self.rollover = position['rollovertm']
        self.terms = position['terms']
        self.time = position['time']
        self.direction = position['type']
        self.volume = position['vol']
        self.volume_closed = position['vol_closed']

        if 'net' in position:
            self.profit = float(position['net'])
        else:
            self.profit = None

    def __str__(self):
        return self.position_id


class Krakencli:
    def __init__(self, key_file):
        """
        Initialize the Krakencli class.

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

        args = {
            'pair': pair,
            'type': direction,
            'ordertype': order_type,
            'volume': '{:.{prec}f}'.format(volume, prec=DEFAULT_PRECISION),
            'price': '{:.{prec}f}'.format(price, prec=DEFAULT_PRECISION),
            'price2': '{:.{prec}f}'.format(price2, prec=DEFAULT_PRECISION),
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
            raise KrakenError(args, result['error'])

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

        if result['error']:
            raise KrakenError(result['error'])

        return Balance(result['result'])

    def get_open_orders(self):
        """
        Get open orders.
        """

        try:
            result = self.k.query_private('OpenOrders')
        except:
            raise

        if result['error']:
            raise KrakenError(result['error'])

        return [Order(order, result['result']['open'][order])
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
            result = self.k.query_private('ClosedOrders', {'start': time})
        except:
            raise

        if result['error']:
            raise KrakenError(result['error'])

        return [Order(order, result['result']['closed'][order])
                for order in result['result']['closed']]

    def get_open_positions(self, docalcs=False, txids=None):
        """
        Get open positions.

        Parameters
        ----------
        docalcs : boolean
            Ask for profit/loss calculation.

        txids : str
            Comma delimited string containing the txids to limit the request to.

        Returns
        -------
        """

        args = {}

        if docalcs:
            args['docalcs'] = docalcs

        if txids:
            args['txid'] = txids

        try:
            result = self.k.query_private('OpenPositions', args)
        except:
            raise

        if result['error']:
            raise KrakenError(args, result['error'])

        return [Position(position, result['result'][position]) for position in result['result']]

    def get_time(self):
        """
        Get the current server time.

        Returns
        -------
        int
            Current UNIX timestamp.
        """

        try:
            result = self.k.query_public('Time')
        except Exception as e:
            raise

        if result['error']:
            raise KrakenError(result['error'])

        return result['result']['unixtime']

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
