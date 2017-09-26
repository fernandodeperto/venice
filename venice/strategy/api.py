class StrategyAPI:
    def __init__(self):

    # Basic info

    def open(self):
        """Current and past open prices."""
        raise NotImplementedError

    def close(self):
        """Current and past close prices."""
        raise NotImplementedError

    def high(self):
        """Current and past high prices."""
        raise NotImplementedError

    def hl2(self):
        """Shortcut for (high + low)/2."""
        raise NotImplementedError

    def hlc3(self):
        """Shortcut for (high + low + close)/3."""
        raise NotImplementedError

    def low(self):
        "Current and past low prices."""
        raise NotImplementedError

    def min_tick(self):
        """Min tick value for the current symbol."""
        raise NotImplementedError

    def ohl4(self):
        """Shortcut for (high + low + open + close)/4."""
        raise NotImplementedError

    def period(self):
        """Candle period in minutes."""
        raise NotImplementedError

    def volume(self):
        """Current and past volume bars."""
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
        """Average entry price of current open positions."""
        raise NotImplementedError

    def closed_trades(self):
        """Number of closed trades for the whole interval."""
        raise NotImplementedError

    def equity(self):
        """Current equity (initial capital + net profit + strategy open profit)."""
        raise NotImplementedError

    def even_trades(self):
        """Number of breakeven trades for the whole trading interval."""
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

    def open_positions(self):
        """Current position entries that are not closed and remain opened."""
        raise NotImplementedError

    def win_trades(self):
        """Number of profitable trades for the whole trading interval."""
        raise NotImplementedError

    # Position

    def cancel(self, name):
        """Command to cancel/deactivate pending orders by referencing their names."""
        raise NotImplementedError

    def cancel_all(self):
        """Command to cancel all pending orders."""
        raise NotImplementedError

    def close(self, name):
        """Command to exit from the position with the specified name."""
        raise NotImplementedError

    def close_all(self):
        """Command to exit from all positions."""
        raise NotImplementedError

    def entry_long(self, name, quantity, limit, stop):
        """Command to enter a long position."""
        raise NotImplementedError

    def entry_short(self, name, quantity, limit, stop):
        """Command to enter a short position."""
        raise NotImplementedError

    # Order

    def order_buy(self, name, quantity, limit, stop):
        """Command to place a buy order."""
        raise NotImplementedError

    def order_sell(self, name, quantity, limit, stop):
        """Command to place a sell order."""
        raise NotImplementedError
