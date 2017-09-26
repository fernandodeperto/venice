from venice.connection.bitfinex import BitfinexConnection

from .api import ExchangeAPI, ExchangeAPIException
from .ohlc import OHLC
from .order import Order
from .position import Position
from .ticker import Ticker

class BitfinexAPI(ExchangeAPI):
    def __init__(self):
        pass

    def add_order(self, pair, direction, type_, volume, price=0, price2=0):
        raise NotImplementedError

    def balance(self):
        raise NotImplementedError

    def cancel_order(self, id_):
        raise NotImplementedError

    def ohlc(self, pair, interval):
        raise NotImplementedError

    def orders(self, pair=None):
        raise NotImplementedError

    def order_history(self, pair=None):
        raise NotImplementedError

    def positions(self, pair=None):
        raise NotImplementedError

    def ticker(self, pair):
        with BitfinexConnection() as c:
            result = c.query_public('pubticker/' + pair)

        return result

