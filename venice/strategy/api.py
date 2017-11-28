from decimal import Decimal
from logging import getLogger

from ..util import decimal_places
from ..api.api import ExchangeAPI


class StrategyAPIError(Exception):
    pass


class StrategyAPI:
    MARKET = ExchangeAPI.MARKET
    LIMIT = ExchangeAPI.LIMIT
    STOP = ExchangeAPI.STOP
    TRAILING_STOP = ExchangeAPI.TRAILING_STOP
    # STOP_AND_LIMIT = ExchangeAPI.STOP_AND_LIMIT

    BUY = ExchangeAPI.BUY
    SELL = ExchangeAPI.SELL

    PENDING = ExchangeAPI.PENDING
    CONFIRMED = ExchangeAPI.CONFIRMED

    def __init__(self, api, pair, period, capital, comission=0):
        self.api = api

        self._pair = pair
        self._period = period
        self._capital = Decimal.from_float(capital)
        self._comission = Decimal.from_float(comission)

        # Only one pending order with each order name
        self.pending_orders = {}

        # Sell order needs to match a closed buy order
        self.buy_orders = {}

        # Get price precision from exchange API
        try:
            self._precision = self.api.pairs[self._pair].precision

        except:
            raise StrategyAPIError

        self._decimal_places = decimal_places(self._precision)

    # Basic info

    def close(self, limit=10):
        return [x.close for x in self.ohlc(limit=limit)]

    def currencies(self):
        return self.api.currencies(self.pair)

    @property
    def DECIMAL_PLACES(self):
        return self._decimal_places

    def high(self, limit=10):
        return [x.high for x in self.ohlc(limit=limit)]

    def hl2(self, limit=10):
        """Shortcut for (high + low)/2."""
        ohlc = self.api.ohlc(self.pair, self.period, limit=limit)
        return [(x.high + x.low)/2 for x in ohlc]

    def hlc3(self, limit=10):
        """Shortcut for (high + low + close)/3."""
        ohlc = self.api.ohlc(self.pair, self.period, limit=limit)
        return [(x.high + x.low + x.close)/3 for x in ohlc]

    def low(self, limit=10):
        return [x.low for x in self.ohlc(limit=limit)]

    def ohl4(self, limit=10):
        """Shortcut for (high + low + open + close)/4."""
        ohlc = self.api.ohlc(self.pair, self.period, limit=limit)
        return [(x.high + x.low + x.open_ + x.close)/4 for x in ohlc]

    def ohlc(self, limit=10):
        """Ticker information."""
        return self.api.ohlc(self.pair, self.period, limit=limit)

    def open(self, limit=10):
        return [x.open_ for x in self.ohlc(limit=limit)]

    @property
    def pair(self):
        """Trading pair."""
        return self._pair

    @property
    def period(self):
        """Candle period in minutes."""
        return self._period

    @property
    def precision(self):
        """Price precision for the current pair."""
        return self._precision

    def ticker(self):
        """Current ticker."""
        return self.api.ticker(self.pair)

    # Comission and balance

    def balance(self):
        ticker = self.ticker()

        used_volume = (sum([x.volume for x in self.buy_orders]) +
                       sum([x.volume for x in self.pending_orders]))
        return self.capital - used_volume * ticker.last

    @property
    def comission(self):
        """Comission percent."""
        return self._comission

    def volume_max(self):
        ticker = self.ticker()
        return self.balance() * (1 - self.comission / 100) / ticker.last

    # Trading statistics

    def avg_price(self):
        """Average entry price of current closed buy orders."""
        raise NotImplementedError

    @property
    def capital(self):
        """The amount of initial capital set in the strategy properties."""
        return self._capital

    def closed_trades(self):
        """Number of closed trades for the whole interval."""
        raise NotImplementedError

    def equity(self):
        """Current equity (initial capital + net profit + strategy open profit)."""
        raise NotImplementedError

    def gross_loss(self):
        """Total currency value of all completed losing trades."""
        raise NotImplementedError

    def gross_profit(self):
        """Total currency value of all completed winning trades."""
        raise NotImplementedError

    def loss_trades(self):
        """Number of unprofitable trades for the whole trading interval."""
        raise NotImplementedError

    def net_profit(self):
        """Total currency value of all completed trades."""
        raise NotImplementedError

    def open_profit(self):
        """Current unrealized profit or loss for the open position."""
        raise NotImplementedError

    def win_trades(self):
        """Number of profitable trades for the whole trading interval."""
        raise NotImplementedError

    # Orders

    def cancel(self, name):
        """Command to cancel/deactivate pending orders by referencing their names."""
        logger = getLogger(__name__)

        if name not in self.pending_orders:
            raise StrategyAPIError('pending order {} not found'.format(name))

        self.api.cancel_order(self.pending_orders[name].id_)

        logger.info('cancel order {}: {}'.format(name, self.pending_orders[name]))

        del self.pending_orders[name]

    def cancel_all(self):
        """Command to cancel all pending orders."""
        for name in list(self.pending_orders.keys()):
            self.cancel(name)

    def order_buy(self, name, type_, volume=0, price=0, price2=0):
        """Place a buy order."""
        if name in self.buy_orders:
            raise StrategyAPIError('buy order {} already exists'.format(name))

        balance = self.balance()
        volume_max = self.volume_max()

        if volume and volume > volume_max():
            raise StrategyAPIError('volume {} is higher than available balance {}/{}'.format(
                volume, balance, volume_max))

        elif not volume:
            volume = volume_max

        return self._order(name, 'buy', type_, volume, price=price, price2=price2)

    def order_sell(self, name, type_, price=0, price2=0):
        """Command to place a sell order."""
        if name not in self.buy_orders:
            raise StrategyAPIError('buy order {} not found'.format(name))

        volume = self.buy_orders[name].volume

        return self.order(name, 'sell', type_, volume, price=price, price2=price2)

    def order_status(self, name):
        if name in self.pending_orders:
            pass

        if name in self.buy_orders:
            pass

        pass

    def update(self):
        logger = getLogger(__name__)

        pending_orders = {}

        for name in self.pending_orders:
            # Try to update a pending order. If it doesn't work, put it back in the list.
            try:
                order_status = self.api.order_status(self.pending_orders[name].id_)

            except:
                pending_orders[name] = self.pending_orders[name]
                return

            if order_status.status == self.OPEN:
                pending_orders[name] = order_status

            elif order_status.status == self.CLOSED:
                if order_status.direction == self.BUY:
                    if name in self.buy_orders:
                        raise StrategyAPIError('buy order {} already exists'.format(name))

                    self.buy_orders[name] = order_status

                else:  # Sell order
                    if name not in self.buy_orders:
                        raise StrategyAPIError('buy order {} not found'.format(name))

                    del self.buy_orders[name]

            elif order_status.status == self.CANCELED:
                raise StrategyAPIError('order {} canceled unexpectedly'.format(name))

            logger.debug('{} order {} {}: {}'.format(
                order_status.direction, name, order_status.status, order_status))

        self.pending_orders = pending_orders

    def clean_up(self):
        for name in list(self.pending_orders.keys()):
            self.cancel(name)

        for name in list(self.buy_orders.keys()):
            self.order_sell(name)

    def _order(self, name, direction, type_, volume, price=0, price2=0):
        logger = getLogger(__name__)

        if name in self.pending_orders:
            self.cancel(name)

        order_statuses = self.api.add_order(
            self.pair, direction, type_, volume=volume, price=price, price2=price2)

        if len(order_statuses) > 1:
            raise StrategyAPIError('orders with multiple order statuses not supported')

        self.pending_orders[name] = order_statuses[0]

        logger.info('new {} order {}: {}'.format(direction, name, self.pending_orders[name]))

        return self.pending_orders[name]
