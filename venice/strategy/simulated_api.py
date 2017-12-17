from logging import getLogger

from .api import StrategyAPI, StrategyAPIError
from ..api.order import Order


class SimulatedStrategyAPI(StrategyAPI):
    def __init__(self, api, pair, period, capital):
        super().__init__(api, pair, period, capital)

    def cancel(self, name):
        """Command to cancel/deactivate pending orders by referencing their names."""
        logger = getLogger(__name__)

        if name not in self.pending_orders:
            raise StrategyAPIError('pending order {} not found'.format(name))

        self.cancelled_orders[name] = self.pending_orders[name]
        self.cancelled_orders[name].status = self.CANCELED
        del self.pending_orders[name]

        logger.debug('cancel order {}: {}'.format(name, self.pending_orders[name]))

    def update(self):
        logger = getLogger(__name__)

        pending_orders = {}

        for name in self.pending_orders:
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

    def _order(self, name, direction, type_, volume, price=0, price2=0):
        logger = getLogger(__name__)

        if name in self.pending_orders:
            self.cancel(name)

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
