from .api import StrategyAPI
from ..api.order import Order


class SimulatedStrategyAPI(StrategyAPI):
    def _cancel_order(self, order_status):
        order_status.status = self.CANCELED

    def _add_order(self, pair, direction, type_, volume=0, price=0, price2=0):
        return self._format_order(
            direction, type_, self.pair, volume, price=price, price2=price2,
            avg_price=(price if type_ == self.LIMIT else self.ticker.last))

    def _update_order(self, order_status):
        ticker = self.ticker

        if order_status.status == self.PENDING:
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
