from collections import namedtuple

from ..api.order import Order

StrategyOrder = namedtuple('StrategyOrder', 'order, status')


class StrategyAPI:
    def __init__(self, api, pair, period, capital, comission=0, live=0):
        self.api = api
        self._pair = pair
        self._period = period
        self._capital = capital
        self._comission = comission
        self.live = live

        self.open_orders = {}

    # Basic info

    def close(self):
        return [x.close for x in self.ohlc()]

    def high(self):
        return [x.high for x in self.ohlc()]

    def hl2(self):
        """Shortcut for (high + low)/2."""
        ohlc = self.api.ohlc(self.pair, self.period)
        return [(x.high + x.low)/2 for x in ohlc]

    def hlc3(self):
        """Shortcut for (high + low + close)/3."""
        ohlc = self.api.ohlc(self.pair, self.period)
        return [(x.high + x.low + x.close)/3 for x in ohlc]

    def low(self):
        return [x.low for x in self.ohlc()]

    def ohl4(self):
        """Shortcut for (high + low + open + close)/4."""
        ohlc = self.api.ohlc(self.pair, self.period)
        return [(x.high + x.low + x.open_ + x.close)/4 for x in ohlc]

    def ohlc(self):
        """Ticker information."""
        return self.api.ohlc(self.pair, self.period)

    def open(self):
        return [x.open_ for x in self.ohlc()]

    @property
    def pair(self):
        """Trading pair."""
        return self._pair

    @property
    def period(self):
        """Candle period in minutes."""
        return self._period

    def ticker(self):
        """Current ticker."""
        return self.api.ticker(self.pair)

    # Comission

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
        if name in self.open_orders:
            result = self.api.cancel_order(self.open_orders[name].order.id_)

    def cancel_all(self):
        """Command to cancel all pending orders."""
        return [self.api.cancel_order(x.order.id_) for x in self.open_orders]

    def order_buy(self, name, quantity, limit=0, stop=0):
        """Command to place a buy order."""

        if name in self.open_orders:
            pass

        return self._order(name, 'buy', quantity, limit, stop)

        return self.open_orders[name].order

    def order_sell(self, name, quantity, limit=0, stop=0):
        """Command to place a sell order."""

        if name in self.open_orders:
            raise ValueError

        self.open_orders[name] = StrategyOrder(
            self._order(name, 'sell', quantity, limit, stop),
            None)

        return self.open_orders[name].order

    # Internal methods

    def _order(self, name, direction, quantity, limit=0, stop=0):
        order_type = (
            (self.api.STOP_AND_LIMIT if stop else self.api.LIMIT) if limit else
            (self.api.STOP if stop else self.api.MARKET))

        if self.live:
            self.open_orders[name] = StrategyOrder(
                self.api.add_order(self.pair, direction, order_type, quantity, limit, stop),
                None)
        else:
            self.open_orders[name] = StrategyOrder(
                Order(-1, direction, order_type, self.pair, quantity, limit, stop),
                None)

        return self.open_orders[name]

    def _update(self):
        for x in self.open_orders:
            x.status = self.api.order_status(x.id_)

        self.open_orders = {x: self.open_orders[x] for x in self.open_orders
                            if x.status == self.api.OPEN}
