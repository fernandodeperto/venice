from logging import getLogger

from ..util import decimal_places


class StrategyAPIError(Exception):
    pass


class StrategyAPI:
    def __init__(self, api, pair, period, capital, comission=0):
        self.api = api

        self._pair = pair
        self._period = period
        self._capital = capital
        self._comission = comission

        # Only one open order with each order name
        self.open_orders = {}

        # Sell order needs to match a closed buy order
        self.buy_orders = {}

        # Get price precision from exchange API
        try:
            self._precision = self.api.pairs[self._pair].precision

        except:
            raise StrategyAPIError

        self._decimal_places = decimal_places(self._precision)

        # Use the same order statuses as the current API's
        self.CANCELED = self.api.CANCELED
        self.CLOSED = self.api.CLOSED
        self.OPEN = self.api.OPEN

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
        return self.api.balance(self.pair)

    @property
    def comission(self):
        """Comission percent."""
        return self._comission

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

        if name not in self.open_orders:
            raise StrategyAPIError('pending order {} not found'.format(name))

        self.api.cancel_order(self.open_orders[name].id_)

        logger.info('cancel order {}: {}'.format(name, self.open_orders[name]))

        del self.open_orders[name]

    def cancel_all(self):
        """Command to cancel all pending orders."""
        for name in self.open_orders:
            self.cancel(name)

    def order(self, name, direction, volume=0, limit=0, stop=0):
        logger = getLogger(__name__)

        if name in self.open_orders:
            self.cancel(name)

        if direction == self.api.BUY and name in self.buy_orders:
            raise StrategyAPIError('buy order {} already exists'.format(name))

        if direction == self.api.SELL and name not in self.buy_orders:
            raise StrategyAPIError('buy order {} not found'.format(name))

        # Limit and stop orders are not supported yet
        if limit and stop:
            raise StrategyAPIError('stop and limit orders not supported')

        if limit:
            price = limit
            price2 = 0
            order_type = self.api.LIMIT

        elif stop:
            price = stop
            price2 = 0
            order_type = self.api.STOP

        else:
            price = 0
            price2 = 0
            order_type = self.api.MARKET

        order_statuses = self.api.add_order(
            self.pair, direction, order_type, volume=volume, price=price, price2=price2)

        if len(order_statuses) > 1:
            raise StrategyAPIError('orders with multiple order statuses not supported')

        logger.info('new {} order {}: {}'.format(direction, name, self.open_orders[name]))

        self.open_orders[name] = order_statuses[0]
        return self.open_orders[name]

    def order_buy(self, name, volume=0, limit=0, stop=0):
        """Command to place a buy order."""
        return self.order(name, 'buy', volume=volume, limit=limit, stop=stop)

    def order_sell(self, name, limit=0, stop=0):
        """Command to place a sell order."""
        if name not in self.buy_orders:
            raise StrategyAPIError('buy order {} not found'.format(name))

        volume = self.buy_orders[name].volume

        return self.order(name, 'sell', volume=volume, limit=limit, stop=stop)

    def order_status(self, name):
        if name in self.open_orders:
            return self.OPEN

        if name in self.buy_orders:
            return self.CLOSED

    def update(self):
        logger = getLogger(__name__)

        open_orders = {}

        for name in self.open_orders:
            # Try to update a pending order. If it doesn't work, put it back in the list.
            try:
                order_status = self.api.order_status(self.open_orders[name].id_)

            except:
                open_orders[name] = self.open_orders[name]
                return

            if order_status.status == self.api.OPEN:
                open_orders[name] = order_status

            elif order_status.status == self.api.CLOSED:
                if order_status.direction == self.api.BUY:
                    if name in self.buy_orders:
                        raise StrategyAPIError('buy order {} already exists'.format(name))

                    self.buy_orders[name] = order_status

                else:  # Sell order
                    if name not in self.buy_orders:
                        raise StrategyAPIError('buy order {} not found'.format(name))

                    del self.buy_orders[name]

            elif order_status.status == self.api.CANCELED:
                raise StrategyAPIError('order {} canceled unexpectedly'.format(name))

            logger.info('{} order {} {}: {}'.format(
                order_status.direction, name, order_status.status, order_status))

        self.open_orders = open_orders

    def clean_up(self):
        while self.buy_orders:
            for name in self.buy_orders:
                order_status = self.api.order_sell(name)

                if order_status.status == self.api.CANCELED:
                    raise StrategyAPIError('order {} cancelled unexpectedly'.format(name))

                elif order_status.status == self.api.CLOSED:
                    del self.buy_orders[name]

                else:
                    self.buy_orders[name] = order_status
