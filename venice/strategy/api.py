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

    NOT_FOUND = None
    PENDING = ExchangeAPI.PENDING
    CONFIRMED = ExchangeAPI.CONFIRMED
    CANCELED = ExchangeAPI.CANCELED

    def __init__(self, api, pair, period, capital):
        self.api = api

        self.pair = pair
        self.period = period
        self.capital = Decimal.from_float(capital)

        self.orders = {}

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
        ohlc = self.api.ohlc(self.pair, self.period, limit=limit)
        return [(x.high + x.low)/2 for x in ohlc]

    def hlc3(self, limit=10):
        ohlc = self.api.ohlc(self.pair, self.period, limit=limit)
        return [(x.high + x.low + x.close)/3 for x in ohlc]

    def low(self, limit=10):
        return [x.low for x in self.ohlc(limit=limit)]

    def ohl4(self, limit=10):
        ohlc = self.api.ohlc(self.pair, self.period, limit=limit)
        return [(x.high + x.low + x.open_ + x.close)/4 for x in ohlc]

    def ohlc(self, limit=10):
        if not self._ohlc or len(self._ohlc) < limit:
            self._ohlc = self.api.ohlc(self.pair, self.period, limit=limit)

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
        used_balance = 0

        for name in self.orders:
            if (self.BUY in self.orders[name] and (
                self.orders[name][self.BUY].status == self.PENDING or
                (self.orders[name][self.BUY].status == self.CONFIRMED and
                 self.SELL in self.orders[name] and
                 self.orders[name][self.SELL].status == self.PENDING))):

                used_balance += self.orders[name][self.BUY].volume

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

        if name in self.orders:
            if (self.BUY in self.orders[name] and
                    self.orders[name][self.BUY].status == self.PENDING):
                self._cancel_order(self.orders[name][self.BUY])
                logger.debug('cancel order {}: {}'.format(name, self.orders[name][self.BUY]))

            elif (self.SELL in self.orders[name] and
                    self.orders[name][self.SELL].status == self.PENDING):
                self._cancel_order(self.orders[name][self.SELL])
                logger.debug('cancel order {}: {}'.format(name, self.orders[name][self.SELL]))

            else:
                raise StrategyAPIError('pending order {} not found'.format(name))

        else:
            StrategyAPIError('order {} not found'.format(name))

    def cancel_all(self):
        """Command to cancel all pending orders."""
        for name in self.orders:
            try:
                self.cancel(name)

            except StrategyAPIError:
                pass

    def order_buy(self, name, type_, volume=0, price=0, price2=0):
        """Place a buy order."""
        if name in self.orders:
            if (self.BUY in self.orders[name] and
                    self.orders[name][self.BUY].status == self.CONFIRMED and
                    self.SELL in self.orders[name] and
                    self.orders[name][self.SELL].status == self.CONFIRMED):
                del self.orders[name]

            elif (self.BUY in self.orders[name] and
                  self.orders[name][self.BUY].status != self.CANCELED):
                raise StrategyAPIError('buy order {} already exists: {}'.format(
                    name, self.orders[name][self.BUY]))

        volume_max = self.volume_max(type_)

        if volume and volume > volume_max:
            raise StrategyAPIError('volume {:.5f} is higher than maximum {:.5f} '.format(
                volume, volume_max))

        elif not volume:
            volume = volume_max

        return self._order(name, 'buy', type_, volume, price=price, price2=price2)

    def order_sell(self, name, type_, price=0, price2=0):
        """Command to place a sell order."""
        if (name not in self.orders or self.BUY not in self.orders[name] or
                self.orders[name][self.BUY].status != self.CONFIRMED):
            raise StrategyAPIError('buy order {} not found'.format(name))

        elif (name in self.orders and self.SELL in self.orders[name] and
              self.orders[name][self.SELL].status != self.CANCELED):
            raise StrategyAPIError('sell order {} already exists: {}'.format(
                name, self.orders[name][self.SELL]))

        volume = self.orders[name][self.BUY].volume

        return self._order(name, 'sell', type_, volume, price=price, price2=price2)

    def order_status(self, name, direction):
        if name in self.orders and direction in self.orders[name]:
            return self.orders[name][direction]

    def update(self):
        logger = getLogger(__name__)

        for order_name in self.orders:
            for order_direction in self.orders[order_name]:
                order_status = self.orders[order_name][order_direction]
                if order_status.status == self.PENDING:
                    self._update_order(order_status)

                    if order_status.status == self.CONFIRMED:
                        maker_fee, taker_fee = self.api.fees()
                        order_fee = (order_status.cost * (maker_fee if order_status.type_ ==
                                                          self.LIMIT else taker_fee))
                        self._balance -= order_fee

                        logger.debug('order fee={:.5f}, balance={:.5f}'.format(
                            order_fee, self._balance))

                        if order_status.direction == self.BUY:
                            logger.info('buy order confirmed, name={}, buy={:.5f}'.format(
                                order_name, order_status.avg_price))

                        else:  # Sell order
                            buy_order = self.orders[order_name][self.BUY]

                            self._balance += order_status.cost - buy_order.cost

                            logger.info(
                                'trade confirmed, name={}, buy={:.5f}, sell={:.5f}, profit={:.5f},'
                                ' balance={:.5f}'.format(
                                    order_name, buy_order.avg_price, order_status.avg_price,
                                    order_status.cost - buy_order.cost, self._balance))

                    self.orders[order_name][order_direction] = order_status

                logger.debug('order {}: {}'.format(
                    order_name, order_status))

        self._ohlc = None
        self._ticker = None

    def clean_up(self):
        for order in self._filter_orders(status=self.PENDING):
            self._cancel_order(order)

        for order in self._filter_orders(direction=self.BUY, status=self.CONFIRMED):
            self._add_order(self.pair, self.SELL, self.MARKET, volume=order.volume)

    # Internal methods

    def _order(self, name, direction, type_, volume, price=0, price2=0):
        logger = getLogger(__name__)

        order_statuses = self._add_order(
            self.pair, direction, type_, volume=volume, price=price, price2=price2)

        if len(order_statuses) > 1:
            raise StrategyAPIError('orders with multiple order statuses not supported')

        if name not in self.orders:
            self.orders[name] = {}

        self.orders[name][direction] = order_statuses[0]

        logger.debug('new {} order {}: {}'.format(direction, name, order_statuses[0]))

        return order_statuses[0]

    def _filter_orders(self, name=None, direction=None, status=None):
        filtered_orders = []

        for order_name in self.orders:
            for order_direction in self.orders[order_name]:
                order_status = self.orders[order_name][order_direction]

                if ((not name or order_name == name) and
                        (not direction or order_status.direction == direction) and
                        (not status or order_status.status == status)):
                    filtered_orders.append(order_status)

        return filtered_orders

    # Parent internal methods

    def _update_order(self, order_status):
        raise NotImplementedError

    def _cancel_order(self, order_status):
        raise NotImplementedError

    def _add_order(self, pair, direction, type_, volume=0, price=0, price2=0):
        raise NotImplementedError
