from .api import StrategyAPI


class LiveStrategyAPI(StrategyAPI):
    def _update_order(self, order_status):
        return self.api.order_status(order_status.id_)

    def _cancel_order(self, order_status):
        self.api.cancel_order(order_status.id_)

    def _add_order(self, *args, **nargs):
        return self.api.add_order(*args, **nargs)
