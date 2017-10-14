from venice.connection.bitfinex import BitfinexConnection

from .api import ExchangeAPI
from .ohlc import OHLC
from .order import Order
from .ticker import Ticker
from .balance import Balance


class BitfinexAPI(ExchangeAPI):
    TYPE_KEYS = {
        ExchangeAPI.MARKET: 'exchange market',
        ExchangeAPI.LIMIT: 'exchange limit',
        ExchangeAPI.STOP: 'exchange stop',
        ExchangeAPI.STOP_AND_LIMIT: 'exchange limit',
    }

    TYPE_KEYS_REVERSE = {
        'exchange market': ExchangeAPI.MARKET,
        'exchange limit': ExchangeAPI.LIMIT,
        'exchange stop': ExchangeAPI.STOP,
    }

    CURRENCY_KEYS = {
        ExchangeAPI.BTC: 'btc',
        ExchangeAPI.ETH: 'eth',
        ExchangeAPI.LTC: 'ltc',
        ExchangeAPI.EUR: 'eur',
        ExchangeAPI.USD: 'usd',
    }

    CURRENCY_KEYS_REVERSE = {
        'btc': ExchangeAPI.BTC,
        'eth': ExchangeAPI.ETH,
        'ltc': ExchangeAPI.LTC,
        'eur': ExchangeAPI.EUR,
        'usd': ExchangeAPI.USD,
    }

    PAIR_KEYS = {
        ExchangeAPI.BTCEUR: 'btceur',
        ExchangeAPI.BTCUSD: 'btcusd',
        ExchangeAPI.ETUEUR: 'etheur',
        ExchangeAPI.ETHUSD: 'ethusd',
        ExchangeAPI.LTCEUR: 'ltceur',
        ExchangeAPI.LTCUSD: 'ltcusd',
    }

    PAIR_KEYS_REVERSE = {
        'btceur': ExchangeAPI.BTCEUR,
        'btcusd': ExchangeAPI.BTCUSD,
        'etheur': ExchangeAPI.ETUEUR,
        'ethusd': ExchangeAPI.ETHUSD,
        'ltceur': ExchangeAPI.LTCEUR,
        'ltcusd': ExchangeAPI.LTCUSD,
    }

    PERIOD_KEYS = {
        ExchangeAPI.P5: '5m',
        ExchangeAPI.P15: '15m',
        ExchangeAPI.P30: '30m',
        ExchangeAPI.P1H: '1h',
        ExchangeAPI.P3H: '3h',
    }

    PERIOD_KEYS_REVERSE = {
        '5m': ExchangeAPI.P5,
        '15m': ExchangeAPI.P15,
        '30m': ExchangeAPI.P30,
        '1h': ExchangeAPI.P1H,
        '3h': ExchangeAPI.P3H,
    }

    DIRECTION_KEYS = {
        ExchangeAPI.BUY: 'buy',
        ExchangeAPI.SELL: 'sell',
    }

    DIRECTION_KEYS_REVERSE = {
        'buy': ExchangeAPI.BUY,
        'sell': ExchangeAPI.SELL,
    }

    def __init__(self):
        pass

    # Public

    def ohlc(self, pair, period, limit=100):
        result = self._candles(
            self.PERIOD_KEYS[period], self._convert_pair(self.PAIR_KEYS[pair]), 'hist',
            limit=limit)
        return [self._format_ohlc(x) for x in result]

    def ticker(self, pair):
        result = self._ticker(pair)
        return self._format_ticker(result)

    # Private

    def active_orders(self, pair=None):
        result = self._active_orders()
        return [self._format_order(x) for x in result if not pair or x['symbol'] == pair]

    def add_order(self, pair, direction, type_, volume, price=0, price2=0):
        oco = type_ == self.STOP_AND_LIMIT and price2 > 0

        result = self._order(
            self.PAIR_KEYS[pair], volume, self.DIRECTION_KEYS[direction], self.TYPE_KEYS[type_],
            price, post_only=True, oco=oco, oco_price=price2)

        orders = [self._format_order(result)]

        if oco:
            orders += [self._format_oco_order(result)]

        return orders

    def balance(self):
        result = self._wallet_balance()

        return [self._format_balance(x) for x in result]

    def cancel_all_orders(self):
        raise NotImplementedError

    def cancel_order(self, id_):
        result = self._cancel_orders([id_])
        return self._format_order_status(result)

    def cancel_orders(self, ids):
        result = self._cancel_orders(ids)
        return self._format_order_status(result)

    def order_history(self, pair=None, limit=100):
        result = self._order_history(limit)
        return [self._format_order(x) for x in result if not pair or x['symbol'] == pair]

    def order_status(self, id_):
        result = self._order_status(id_)
        return self._format_order(result)

    # v1 endpoints - public

    def _ticker(self, pair):
        """Return ticker.

        Fields
        =====

        mid        [price] (bid + ask) / 2
        bid        [price] Innermost bid
        ask        [price] Innermost ask
        last_price [price] The price at which the last order executed
        low        [price] Lowest trade price of the last 24 hours
        high       [price] Highest trade price of the last 24 hours
        volume     [price] Trading volume of the last 24 hours
        timestamp  [time]  The timestamp at which this information was valid
        """

        with BitfinexConnection() as c:
            return c.query_public('pubticker/' + pair)

    # v1 endpoints - private

    def _active_orders(self):
        """View active orders."""
        with BitfinexConnection() as c:
            return c.query_private('orders')

    def _cancel_orders(self, order_ids):
        """Cancel an order.

        Params
        ======

        order_ids : int[]
        """

        with BitfinexConnection() as c:
            return c.query_private('order/cancel/multi', params={
                'order_ids': order_ids,
            })

    def _order(self, pair, amount, side, type_, price=0, hidden=False, post_only=False,
               use_all=False, oco=False, oco_price=0):
        """Submit a new order.

        Params
        ======

        symbol : str

        amount : float

        side : str
            Either 'buy' or 'sell'.

        type : str
            Can be: "market" / "limit" / "stop" / "trailing-stop" / "fill-or-kill" / "exchange
            market" / "exchange limit" / "exchange stop" / "exchange trailing-stop" / "exchange
            fill-or-kill". (type starting by "exchange" are exchange orders, others are margin
            trading orders)

        price : float

        is_hidden : boolean
            True if order should be hidden.

        is_postonly : boolean
            True if order should be post only. Only relevant for limit orders.

        use_all_available : int
            If 1 post an order that will use all your available balance.

        ocoorder : boolean
            Set an additional STOP OCO order that will be linked with the current order.

        buy_price_oco: float
            If ocoorder is true, this field represents the price of the OCO stop order to place.

        sell_price_oco: float
            If ocoorder is true, this field represents the price of the OCO stop order to place.

        Fields
        ======

        order_id : int
            An order object containing the order ID as well as all the information privided by
            /order/status.
        """

        params = {
            'symbol': pair,
            'amount': str(amount),
            'side': side,
            'type': type_,
            'price': str(price),
            'is_hidden': hidden,
            'is_postonly': post_only,
            'use_all_available': use_all,
            'ocoorder': oco,
            'buy_price_oco': str(oco_price) if oco and side == 'buy' else '0',
            'sell_price_oco': str(oco_price) if oco and side == 'sell' else '0',
        }

        with BitfinexConnection() as c:
            return c.query_private('order/new', params=params)

    def _order_history(self, limit=100):
        """View latest inactive orders.

        Limited to 3 days and 1 request per minute.

        Params
        ======

        limit : int
            Limit number of results
        """

        with BitfinexConnection() as c:
            return c.query_private('orders/hist', params={'limit_orders': limit})

    def _order_status(self, id_):
        """Get the status of an order.

        Params
        ======

        order_id : int
            The order ID given by /order/new.

        Fields
        ======

        symbol              [string]    The symbol name the order belongs to
        exchange            [string]    "bitfinex"
        price               [decimal]   The price the order was issued at (can be null for market orders)
        avg_execution_price [decimal]   The average price at which this order as been executed so
                                        far. 0 if the order has not been executed at all
        side                [string]    Either "buy" or "sell"
        type                [string]    Either "market" / "limit" / "stop" / "trailing-stop"
        timestamp           [time]      The timestamp the order was submitted
        is_live             [bool]      Could the order still be filled?
        is_cancelled        [bool]      Has the order been cancelled?
        is_hidden           [bool]      Is the order hidden?
        oco_order           [int64]     If the order is an OCO order, the ID of the linked order. Otherwise,
        null
        was_forced          [bool]      For margin only true if it was forced by the system
        executed_amount     [decimal]   How much of the order has been executed so far in its history?
        remaining_amount    [decimal]   How much is still remaining to be submitted?
        original_amount     [decimal]   What was the order originally submitted for?
        """

        with BitfinexConnection() as c:
            return c.query_private('order/status', params={
                'order_id': id_,
            })

    def _wallet_balance(self):
        """Return wallet balances."""

        with BitfinexConnection() as c:
            return c.query_private('balances')

    # v2 endpoints - public

    def _candles(self, time_frame, pair, section, limit=100, start='', end='', sort=0):
        """Return charter candle info.

        Path params
        ===========

        time_frame: string
            Available values: '1m', '5m', '15m', '30m', '1h', '3h', '6h', '12h', '1D', '7D', '14D',
            '1M'.

        symbol: string
            The symbol you want information about.

        section: string
            Available values: last, hist.

        Query params
        ============

        limit: int
            Number of candles requested.

        start: string
            Filter start (ms).

        end: string
            Filter end (ms).

        sort: int
            Sorts results returned with old > new if 1

        Fields
        =====

        MTS     [int]   millisecond time stamp
        OPEN    [float] First execution during the time frame
        CLOSE   [float] Last execution during the time frame
        HIGH    [float] Highest execution during the time frame
        LOW     [float] Lowest execution during the timeframe
        VOLUME  [float] Quantity of symbol traded within the timeframe
        """

        params = {
            'limit': limit,
        }

        with BitfinexConnection(version='v2') as c:
            return c.query_public(
                'candles/trade:' + ':'.join([time_frame, pair]) + '/' + section, get_params=params)
        return 't' + pair.upper()

    # v2 endpoints - private

    # Internal methods

    @staticmethod
    def _convert_pair(pair):
        return 't' + pair.upper()

    @staticmethod
    def _format_order(result):
        status = (
            ExchangeAPI.OPEN if result['is_live'] else
            ExchangeAPI.CANCELED if result['is_cancelled'] else ExchangeAPI.CLOSED)

        return Order(
            result['id'],
            result['side'],
            BitfinexAPI.TYPE_KEYS_REVERSE[result['type']],
            BitfinexAPI.PAIR_KEYS_REVERSE[result['symbol']],
            status,
            result['original_amount'],
            price=result['price'],
            avg_price=result['avg_execution_price'],
            remaining=result['remaining_amount'])

    @staticmethod
    def _format_oco_order(result):
        return Order(
            result['oco_order'],
            result['side'],
            ExchangeAPI.STOP,
            BitfinexAPI.PAIR_KEYS_REVERSE[result['symbol']],
            result['original_amount'])

    @staticmethod
    def _format_balance(result):
        return Balance(
            BitfinexAPI.CURRENCY_KEYS_REVERSE[result['currency']], result['amount'],
            result['available'], result['type'])

    @staticmethod
    def _format_ticker(result):
        return Ticker(
            result['timestamp'], result['ask'], result['bid'], result['last_price'],
            low=result['low'], high=result['high'], volume=result['volume'])

    @staticmethod
    def _format_ohlc(result):
        return OHLC(result[0], result[1], result[3], result[4], result[2], result[5])
