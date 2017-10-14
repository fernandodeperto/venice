class ExchangeAPIException(Exception):
    pass


class ExchangeAPI:
    # Order types
    MARKET = 'market'
    LIMIT = 'limit'
    STOP = 'stop'
    STOP_AND_LIMIT = 'stop_and_limit'

    # Currencies
    BTC = 'btc'
    ETH = 'eth'
    LTC = 'ltc'
    EUR = 'eur'
    USD = 'usd'

    # Pairs
    BTCEUR = 'btceur'
    BTCUSD = 'btcusd'
    ETUEUR = 'etheur'
    ETHUSD = 'ethusd'
    LTCEUR = 'ltceur'
    LTCUSD = 'ltcusd'

    # Candle period
    P5 = '5'
    P15 = '15'
    P30 = '30'
    P1H = '1h'
    P3H = '3h'
    P4H = '4h'

    # Order direction
    BUY = 'buy'
    SELL = 'sell'

    # Order status
    OPEN = 'open'
    CLOSED = 'closed'
    CANCELED = 'cancelled'

    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        pass

    def active_orders(self, pair=None):
        raise NotImplementedError

    def add_order(self, pair, direction, type_, volume, price=0, price2=0):
        raise NotImplementedError

    def balance(self):
        raise NotImplementedError

    def cancel_all_orders(self):
        raise NotImplementedError

    def cancel_order(self, id_):
        raise NotImplementedError

    def cancel_orders(self, ids):
        raise NotImplementedError

    def ohlc(self, pair, interval, limit=100):
        raise NotImplementedError

    def order_history(self, pair=None, limit=100):
        raise NotImplementedError

    def order_status(self, id_):
        raise NotImplementedError

    def ticker(self, pair):
        raise NotImplementedError
