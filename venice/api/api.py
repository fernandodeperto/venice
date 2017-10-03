class ExchangeAPIException(Exception):
    pass


class ExchangeAPI:
    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
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
        raise NotImplementedError

    def time(self):
        raise NotImplementedError
