class StrategyAPI:
    def __init__(self):
        pass

    # Basic info

    def hl2(self):
        """Shortcut for (high + low)/2."""
        raise NotImplementedError

    def hlc3(self):
        """Shortcut for (high + low + close)/3."""
        raise NotImplementedError

    def ohl4(self):
        """Shortcut for (high + low + open + close)/4."""
        raise NotImplementedError

    def ohlc(self):
        """Ticker information."""
        raise NotImplementedError

    def period(self):
        """Candle period in minutes."""
        raise NotImplementedError

    def vwap(self):
        """Volume-weighted average price. Uses hlc3 as a source series."""
        raise NotImplementedError

    # Comission

    def comission_percent(self):
        """Comission percent."""
        raise NotImplementedError

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

    def initial_capital(self):
        """The amount of initial capital set in the strategy properties."""
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
        raise NotImplementedError

    def cancel_all(self):
        """Command to cancel all pending orders."""
        raise NotImplementedError

    def order_buy(self, name, quantity, limit, stop):
        """Command to place a buy order."""
        raise NotImplementedError

    def order_sell(self, name, quantity, limit, stop):
        """Command to place a sell order."""
        raise NotImplementedError
