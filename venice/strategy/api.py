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
    CANCELED = ExchangeAPI.CANCELED

    OHLC_DEFAULT_LIMIT = 100

    def __init__(self, api, pair, period, capital, live=True):
        self.api = api

        self.pair = pair
        self.period = period
        self.capital = Decimal.from_float(capital)
        self.live = live

        self.pending_orders = {}
        self.buy_orders = {}
        self.sell_orders = {}
        self.cancelled_orders = {}

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
        used_balance = sum([x.cost for x in list(self.pending_orders.values()) +
                            list(self.buy_orders.values())])
        return self._balance - used_balance, self._balance

    def volume_max(self, type_):
        maker_fee, taker_fee = self.api.fees()
        return (self.balance[0] * (1 - (maker_fee if type_ == self.LIMIT else taker_fee)) /
                self.ticker.last)

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
        else:
            self.pending_orders[name].status = self.CANCELED

        logger.debug('cancel order {}: {}'.format(name, self.pending_orders[name]))

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

        volume_max = self.volume_max(type_)

        if volume and volume > volume_max:
            raise StrategyAPIError('volume {:.5f} is higher than maximum {:.5f} '.format(
                volume, volume_max))

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

        if name in self.cancelled_orders:
            return self.CANCELED

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

                    logger.info('buy order confirmed, name={}, buy={:.5f}'.format(
                        name, order_status.avg_price))

                else:  # Sell order
                    if name not in self.buy_orders:
                        raise StrategyAPIError('buy order {} not found'.format(name))

                    self._balance += order_status.cost - self.buy_orders[name].cost

                    logger.info(
                        'trade confirmed, name={}, buy={:.5f}, sell={:.5f}, profit={:.5f},'
                        ' balance={:.5f}'.format(
                            name, self.buy_orders[name].avg_price, order_status.avg_price,
                            order_status.cost - self.buy_orders[name].cost, self._balance))

                    self.sell_orders[name] = order_status
                    del self.buy_orders[name]

                maker_fee, taker_fee = self.api.fees()
                order_fee = (order_status.cost *
                             (maker_fee if order_status.type_ == self.LIMIT else taker_fee))
                self._balance -= order_fee

                logger.debug('order fee={:.5f}, balance={:.5f}'.format(order_fee, self._balance))

            elif order_status.status == self.CANCELED:
                self.cancelled_orders = order_status

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
                avg_price=(price if type_ == self.LIMIT else self.ticker.last))

        if len(order_statuses) > 1:
            raise StrategyAPIError('orders with multiple order statuses not supported')

        self.pending_orders[name] = order_statuses[0]

        logger.debug('new {} order {}: {}'.format(direction, name, self.pending_orders[name]))

        return self.pending_orders[name]

    def _order_status(self, order_status):
        ticker = self.ticker

        if order_status.type_ == self.MARKET:
            order_status.status = self.CONFIRMED
            order_status.executed_volume = order_status.volume

        elif (order_status.type_ == self.LIMIT and
              ((order_status.direction == self.BUY and ticker.last <= order_status.price) or
               (order_status.direction == self.SELL and ticker.last >= order_status.price))):
            order_status.status = self.CONFIRMED
            order_status.executed_volume = order_status.volume

        elif (order_status.type_ == self.STOP and
              ((order_status.direction == self.BUY and ticker.last >= order_status.price) or
               (order_status.direction == self.SELL and ticker.last <= order_status.price))):
            order_status.status = self.CONFIRMED
            order_status.executed_volume = order_status.volume

        return order_status

    def _format_order(self, direction, type_, pair, volume, price=0, price2=0, avg_price=None,
                      remaining=None, pivot=None):
        return [Order(
            -1, direction, type_, pair, self.PENDING, volume, 0, price=price, price2=price2,
            avg_price=avg_price, remaining=remaining, pivot=pivot)]
