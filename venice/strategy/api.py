from decimal import Decimal
from logging import getLogger

from ..util import decimal_places
from ..api.api import ExchangeAPI
from ..api.order import Order


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

    NOT_FOUND = ''
    PENDING = ExchangeAPI.PENDING
    CONFIRMED = ExchangeAPI.CONFIRMED

    OHLC_DEFAULT_LIMIT = 100

    def __init__(self, api, pair, period, capital, comission=0, live=True):
        self.api = api

        self.pair = pair
        self.period = period
        self.capital = Decimal.from_float(capital)
        self.comission = Decimal.from_float(comission)
        self.live = live

        # Only one pending order with each order name
        self.pending_orders = {}

        # Sell order needs to match a closed buy order
        self.buy_orders = {}

        # Confirmed sell orers
        self.sell_orders = {}

        # Properties
        self._precision = None
        self._decimal_places = None
        self._balance = Decimal.from_float(capital)

        # Caching
        self._ohlc = None
        self._ticker = None

    # Basic info

    def close(self, limit=10):
        return [x.close for x in self.ohlc(limit=limit)]

    def currencies(self):
        return self.api.currencies(self.pair)

    @property
    def decimal_places(self):
        if not self._decimal_places:
            self._decimal_places = decimal_places(self.precision)

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
        if limit > self.OHLC_DEFAULT_LIMIT:
            raise StrategyAPIError('limit {} exceeds maximum {}'.format(
                limit, self.OHLC_DEFAULT_LIMIT))

        if not self._ohlc:
            self._ohlc = self.api.ohlc(self.pair, self.period, limit=self.OHLC_DEFAULT_LIMIT)

        return self._ohlc[-limit:]

    def open(self, limit=10):
        return [x.open_ for x in self.ohlc(limit=limit)]

    @property
    def precision(self):
        """Price precision for the current pair."""
        if not self._precision:
            self._precision = self.api.pairs[self.pair].precision

        return self._precision

    @property
    def ticker(self):
        """Current ticker."""
        if not self._ticker:
            self._ticker = self.api.ticker(self.pair)

        return self._ticker

    # Comission and balance

    @property
    def balance(self):
        return self._balance - sum(
            [x.cost for x in list(self.pending_orders.values()) + list(self.buy_orders.values())])

    def volume_max(self):
        ticker = self.ticker
        return self.balance * (1 - self.comission / 100) / ticker.last

    # Trading statistics

    def avg_price(self):
        """Average entry price of current closed buy orders."""
        raise NotImplementedError

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

        if self.live:
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

        if name in self.sell_orders:
            del self.sell_orders[name]

        volume_max = self.volume_max()

        if volume and volume > volume_max():
            raise StrategyAPIError('volume {} is higher than available balance {}/{}'.format(
                volume, self.balance, volume_max))

        elif not volume:
            volume = volume_max

        return self._order(name, 'buy', type_, volume, price=price, price2=price2)

    def order_sell(self, name, type_, price=0, price2=0):
        """Command to place a sell order."""
        if name not in self.buy_orders:
            raise StrategyAPIError('buy order {} not found'.format(name))

        volume = self.buy_orders[name].volume

        return self._order(name, 'sell', type_, volume, price=price, price2=price2)

    def order_status(self, name):
        if name in self.pending_orders:
            return self.PENDING

        if name in self.buy_orders or name in self.sell_orders:
            return self.CONFIRMED

        return self.NOT_FOUND

    def update(self):
        logger = getLogger(__name__)

        pending_orders = {}

        for name in self.pending_orders:
            if self.live:
                try:
                    order_status = self.api.order_status(self.pending_orders[name].id_)

                except Exception:
                    pending_orders[name] = self.pending_orders[name]
                    raise

            else:
                order_status = self._order_status(self.pending_orders[name])

            if order_status.status == self.PENDING:
                pending_orders[name] = order_status

            elif order_status.status == self.CONFIRMED:
                if order_status.direction == self.BUY:
                    if name in self.buy_orders:
                        raise StrategyAPIError('buy order {} already exists'.format(name))

                    self.buy_orders[name] = order_status

                    logger.info('buy order confirmed, name={}, buy={}'.format(
                        name, order_status.avg_price))

                else:  # Sell order
                    if name not in self.buy_orders:
                        raise StrategyAPIError('buy order {} not found'.format(name))

                    self._balance += order_status.cost - self.buy_orders[name].cost

                    logger.info(
                        'trade confirmed, name={}, buy={}, sell={}, profit={},'
                        ' balance={}'.format(
                            name, self.buy_orders[name].avg_price, order_status.avg_price,
                            order_status.cost - self.buy_orders[name].cost, self._balance))

                    del self.buy_orders[name]
                    self.sell_orders[name] = order_status

            elif order_status.status == self.CANCELED:
                raise StrategyAPIError('order {} canceled unexpectedly'.format(name))

            logger.debug('order {} {}: {}'.format(
                name, order_status.status, order_status))

        self.pending_orders = pending_orders

        self._ohlc = None
        self._ticker = None

    def clean_up(self):
        for name in list(self.pending_orders.keys()):
            self.cancel(name)

        for name in list(self.buy_orders.keys()):
            self.order_sell(name, self.MARKET)

    def _order(self, name, direction, type_, volume, price=0, price2=0):
        logger = getLogger(__name__)

        if name in self.pending_orders:
            self.cancel(name)

        if self.live:
            order_statuses = self.api.add_order(
                self.pair, direction, type_, volume=volume, price=price, price2=price2)

        else:
            order_statuses = self._format_order(
                direction, type_, self.pair, volume, price=price, price2=price2,
                avg_price=self.ticker.last)

        if len(order_statuses) > 1:
            raise StrategyAPIError('orders with multiple order statuses not supported')

        self.pending_orders[name] = order_statuses[0]

        logger.debug('new {} order {}: {}'.format(direction, name, self.pending_orders[name]))

        return self.pending_orders[name]

    def _order_status(self, order_status):
        ticker = self.ticker

        if order_status.type_ == self.MARKET:
            order_status.status = self.CONFIRMED

        elif (order_status.type_ == self.LIMIT and
              ((order_status.direction == self.buy and ticker.last <= order_status.price) or
               (order_status.direction == self.sell and ticker.last >= order_status.price))):
            order_status.status = self.CONFIRMED

        elif (order_status.type_ == self.STOP and
              ((order_status.direction == self.BUY and ticker.last >= order_status.price) or
               (order_status.direction == self.SELL and ticker.last <= order_status.price))):
            order_status.status = self.CONFIRMED

        elif order_status.type_ == self.TRAILING_STOP:
            if order_status.direction == self.BUY:
                order_status.pivot = min(order_status.pivot, ticker.last)

                if ticker.last >= order_status.pivot + order_status.price2:
                    order_status.status = self.CONFIRMED
            else:
                order_status.pivot = max(order_status.pivot, ticker.last)

                if ticker.last <= order_status.pivot - order_status.price2:
                    order_status.status = self.CONFIRMED

        # TODO fix the avg price if order type is not limit

        return order_status

    def _format_order(self, direction, type_, pair, volume, price=0, price2=0, avg_price=None,
                      remaining=None, pivot=None):
        return [Order(
            -1, direction, type_, pair, self.PENDING, volume, price=price, price2=price2,
            avg_price=avg_price, remaining=remaining, pivot=pivot)]
